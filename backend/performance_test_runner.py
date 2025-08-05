#!/usr/bin/env python3
"""
Performance Test Runner for Heario News Search

This script performs comprehensive performance testing including:
1. Multiple concurrent search requests
2. Load testing scenarios
3. Bottleneck identification
4. Performance regression testing

Usage:
    python performance_test_runner.py [options]
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import argparse
import concurrent.futures
import threading
import sys
import os

class PerformanceTestRunner:
    def __init__(self, base_url: str = 'http://localhost:5000/api', log_file: str = 'load_test_results.log'):
        self.base_url = base_url
        self.log_file = log_file
        self.results = []
        
    async def single_search_request(self, session: aiohttp.ClientSession, query: str, request_id: int) -> Dict[str, Any]:
        """Perform a single search request and measure performance"""
        start_time = time.time()
        
        try:
            # Step 1: Trigger news fetch
            fetch_start = time.time()
            async with session.post(
                f'{self.base_url}/news/fetch',
                json={'query': query},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                fetch_data = await response.json()
                fetch_time = time.time() - fetch_start
                fetch_success = response.status == 200
            
            # Step 2: Get news list
            get_start = time.time()
            async with session.get(
                f'{self.base_url}/news?limit=20',
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                news_data = await response.json()
                get_time = time.time() - get_start
                get_success = response.status == 200
            
            total_time = time.time() - start_time
            
            result = {
                'request_id': request_id,
                'query': query,
                'success': fetch_success and get_success,
                'total_time': total_time,
                'fetch_time': fetch_time,
                'get_time': get_time,
                'fetch_response': fetch_data if fetch_success else None,
                'news_count': len(news_data) if get_success and isinstance(news_data, list) else 0,
                'timestamp': datetime.now().isoformat(),
                'errors': []
            }
            
            if not fetch_success:
                result['errors'].append(f"Fetch failed with status {response.status}")
            if not get_success:
                result['errors'].append(f"Get news failed with status {response.status}")
                
            return result
            
        except asyncio.TimeoutError:
            total_time = time.time() - start_time
            return {
                'request_id': request_id,
                'query': query,
                'success': False,
                'total_time': total_time,
                'error': 'Request timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            total_time = time.time() - start_time
            return {
                'request_id': request_id,
                'query': query,
                'success': False,
                'total_time': total_time,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def concurrent_requests_test(self, queries: List[str], concurrent_requests: int = 3) -> Dict[str, Any]:
        """Test multiple concurrent search requests"""
        print(f"Running concurrent requests test with {concurrent_requests} requests...")
        
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=180)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for concurrent requests
            tasks = []
            for i in range(concurrent_requests):
                query = queries[i % len(queries)]
                task = self.single_search_request(session, query, i)
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Process results
            successful_results = []
            failed_results = []
            
            for result in results:
                if isinstance(result, Exception):
                    failed_results.append({
                        'error': str(result),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    if result.get('success'):
                        successful_results.append(result)
                    else:
                        failed_results.append(result)
            
            return {
                'test_type': 'concurrent_requests',
                'concurrent_requests': concurrent_requests,
                'total_time': end_time - start_time,
                'successful_requests': len(successful_results),
                'failed_requests': len(failed_results),
                'success_rate': len(successful_results) / concurrent_requests if concurrent_requests > 0 else 0,
                'results': successful_results,
                'failures': failed_results,
                'timestamp': datetime.now().isoformat()
            }
    
    def sequential_requests_test(self, queries: List[str], num_requests: int = 5) -> Dict[str, Any]:
        """Test sequential search requests to establish baseline"""
        print(f"Running sequential requests test with {num_requests} requests...")
        
        import requests
        results = []
        
        for i in range(num_requests):
            query = queries[i % len(queries)]
            print(f"Processing request {i+1}/{num_requests}: {query}")
            
            start_time = time.time()
            
            try:
                # Step 1: Trigger news fetch
                fetch_start = time.time()
                fetch_response = requests.post(
                    f'{self.base_url}/news/fetch',
                    json={'query': query},
                    timeout=120
                )
                fetch_time = time.time() - fetch_start
                fetch_success = fetch_response.status_code == 200
                
                # Step 2: Get news list
                get_start = time.time()
                get_response = requests.get(
                    f'{self.base_url}/news?limit=20',
                    timeout=30
                )
                get_time = time.time() - get_start
                get_success = get_response.status_code == 200
                
                total_time = time.time() - start_time
                
                result = {
                    'request_id': i,
                    'query': query,
                    'success': fetch_success and get_success,
                    'total_time': total_time,
                    'fetch_time': fetch_time,
                    'get_time': get_time,
                    'fetch_response': fetch_response.json() if fetch_success else None,
                    'news_count': len(get_response.json()) if get_success else 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(result)
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                total_time = time.time() - start_time
                results.append({
                    'request_id': i,
                    'query': query,
                    'success': False,
                    'total_time': total_time,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        successful_results = [r for r in results if r.get('success')]
        
        return {
            'test_type': 'sequential_requests',
            'total_requests': num_requests,
            'successful_requests': len(successful_results),
            'failed_requests': num_requests - len(successful_results),
            'success_rate': len(successful_results) / num_requests,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def stress_test(self, query: str = '台灣', duration_seconds: int = 60, requests_per_second: int = 1) -> Dict[str, Any]:
        """Perform stress test with sustained load"""
        print(f"Running stress test for {duration_seconds}s at {requests_per_second} req/s...")
        
        import requests
        import threading
        
        results = []
        results_lock = threading.Lock()
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def make_request(request_id: int):
            req_start = time.time()
            try:
                response = requests.post(
                    f'{self.base_url}/news/fetch',
                    json={'query': query},
                    timeout=30
                )
                req_time = time.time() - req_start
                
                with results_lock:
                    results.append({
                        'request_id': request_id,
                        'success': response.status_code == 200,
                        'duration': req_time,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                req_time = time.time() - req_start
                with results_lock:
                    results.append({
                        'request_id': request_id,
                        'success': False,
                        'duration': req_time,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        request_id = 0
        interval = 1.0 / requests_per_second
        
        while time.time() < end_time:
            thread = threading.Thread(target=make_request, args=(request_id,))
            thread.start()
            request_id += 1
            
            # Wait for next request
            time.sleep(interval)
        
        # Wait for all threads to complete
        time.sleep(10)
        
        successful_results = [r for r in results if r.get('success')]
        
        return {
            'test_type': 'stress_test',
            'duration_seconds': duration_seconds,
            'target_rps': requests_per_second,
            'total_requests': len(results),
            'successful_requests': len(successful_results),
            'failed_requests': len(results) - len(successful_results),
            'actual_rps': len(results) / duration_seconds,
            'success_rate': len(successful_results) / len(results) if results else 0,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_bottlenecks(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test results to identify bottlenecks"""
        print("Analyzing performance bottlenecks...")
        
        all_successful_results = []
        
        for test in test_results:
            if test.get('results'):
                successful = [r for r in test['results'] if r.get('success')]
                all_successful_results.extend(successful)
        
        if not all_successful_results:
            return {
                'analysis': 'No successful requests to analyze',
                'timestamp': datetime.now().isoformat()
            }
        
        # Extract timing data
        total_times = [r.get('total_time', 0) for r in all_successful_results if r.get('total_time')]
        fetch_times = [r.get('fetch_time', 0) for r in all_successful_results if r.get('fetch_time')]
        get_times = [r.get('get_time', 0) for r in all_successful_results if r.get('get_time')]
        
        # Calculate statistics
        analysis = {
            'total_requests_analyzed': len(all_successful_results),
            'timing_analysis': {},
            'bottleneck_identification': {},
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if total_times:
            analysis['timing_analysis']['total_time'] = {
                'mean': statistics.mean(total_times),
                'median': statistics.median(total_times),
                'min': min(total_times),
                'max': max(total_times),
                'p95': sorted(total_times)[int(len(total_times) * 0.95)] if len(total_times) > 1 else total_times[0],
                'stdev': statistics.stdev(total_times) if len(total_times) > 1 else 0
            }
        
        if fetch_times:
            analysis['timing_analysis']['fetch_time'] = {
                'mean': statistics.mean(fetch_times),
                'median': statistics.median(fetch_times),
                'min': min(fetch_times),
                'max': max(fetch_times),
                'p95': sorted(fetch_times)[int(len(fetch_times) * 0.95)] if len(fetch_times) > 1 else fetch_times[0],
                'stdev': statistics.stdev(fetch_times) if len(fetch_times) > 1 else 0
            }
        
        if get_times:
            analysis['timing_analysis']['get_time'] = {
                'mean': statistics.mean(get_times),
                'median': statistics.median(get_times),
                'min': min(get_times),
                'max': max(get_times),
                'p95': sorted(get_times)[int(len(get_times) * 0.95)] if len(get_times) > 1 else get_times[0],
                'stdev': statistics.stdev(get_times) if len(get_times) > 1 else 0
            }
        
        # Bottleneck identification
        if fetch_times and get_times:
            avg_fetch = statistics.mean(fetch_times) 
            avg_get = statistics.mean(get_times)
            
            analysis['bottleneck_identification'] = {
                'primary_bottleneck': 'news_fetch' if avg_fetch > avg_get else 'news_retrieval',
                'fetch_vs_get_ratio': avg_fetch / avg_get if avg_get > 0 else float('inf'),
                'fetch_percentage': (avg_fetch / (avg_fetch + avg_get)) * 100 if (avg_fetch + avg_get) > 0 else 0
            }
            
            if avg_fetch > avg_get * 2:
                analysis['recommendations'].append("News fetching (including Jina AI and summarization) is the primary bottleneck")
                analysis['recommendations'].append("Consider optimizing Jina AI timeout settings or implementing caching")
                analysis['recommendations'].append("Consider parallel processing of Jina AI requests")
            elif avg_get > avg_fetch * 2:
                analysis['recommendations'].append("News retrieval from database is the bottleneck")
                analysis['recommendations'].append("Consider database indexing optimization")
            else:
                analysis['recommendations'].append("Performance is relatively balanced between components")
        
        # Performance recommendations based on response times
        if total_times:
            avg_total = statistics.mean(total_times)
            if avg_total > 30:
                analysis['recommendations'].append("Average response time is very high (>30s) - urgent optimization needed")
            elif avg_total > 15:
                analysis['recommendations'].append("Average response time is high (>15s) - optimization recommended")
            elif avg_total > 5:
                analysis['recommendations'].append("Average response time is moderate (>5s) - minor optimization may help")
        
        return analysis
    
    def run_comprehensive_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive performance test suite"""
        print("Starting comprehensive performance test suite...")
        
        queries = test_config.get('queries', ['台灣', 'AI', '科技', '經濟'])
        
        all_results = []
        
        # Test 1: Sequential requests (baseline)
        if test_config.get('run_sequential', True):
            sequential_result = self.sequential_requests_test(
                queries, 
                test_config.get('sequential_requests', 3)
            )
            all_results.append(sequential_result)
            print(f"Sequential test completed: {sequential_result['success_rate']:.1%} success rate")
        
        # Test 2: Concurrent requests
        if test_config.get('run_concurrent', True):
            concurrent_result = asyncio.run(self.concurrent_requests_test(
                queries,
                test_config.get('concurrent_requests', 3)
            ))
            all_results.append(concurrent_result)
            print(f"Concurrent test completed: {concurrent_result['success_rate']:.1%} success rate")
        
        # Test 3: Stress test (optional)
        if test_config.get('run_stress_test', False):
            stress_result = self.stress_test(
                query=queries[0],
                duration_seconds=test_config.get('stress_duration', 30),
                requests_per_second=test_config.get('stress_rps', 1)
            )
            all_results.append(stress_result)
            print(f"Stress test completed: {stress_result['success_rate']:.1%} success rate")
        
        # Analyze bottlenecks
        bottleneck_analysis = self.analyze_bottlenecks(all_results)
        
        comprehensive_result = {
            'test_suite': 'comprehensive_performance_test',
            'test_config': test_config,
            'individual_tests': all_results,
            'bottleneck_analysis': bottleneck_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        results_file = f'comprehensive_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_result, f, indent=2, ensure_ascii=False)
        
        print(f"Comprehensive test completed. Results saved to {results_file}")
        
        # Print summary
        self.print_comprehensive_summary(comprehensive_result)
        
        return comprehensive_result
    
    def print_comprehensive_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "="*100)
        print("COMPREHENSIVE PERFORMANCE TEST SUMMARY")
        print("="*100)
        
        # Test overview
        individual_tests = results.get('individual_tests', [])
        print(f"Tests Run: {len(individual_tests)}")
        
        for test in individual_tests:
            test_type = test.get('test_type', 'unknown')
            success_rate = test.get('success_rate', 0)
            print(f"  {test_type}: {success_rate:.1%} success rate")
        
        # Bottleneck analysis
        analysis = results.get('bottleneck_analysis', {})
        timing_analysis = analysis.get('timing_analysis', {})
        
        print("\nPERFORMANCE METRICS:")
        print("-" * 50)
        
        for metric, stats in timing_analysis.items():
            if isinstance(stats, dict):
                print(f"\n{metric.replace('_', ' ').title()}:")
                print(f"  Mean:     {stats.get('mean', 0):.2f}s")
                print(f"  Median:   {stats.get('median', 0):.2f}s")
                print(f"  95th %:   {stats.get('p95', 0):.2f}s")
                print(f"  Max:      {stats.get('max', 0):.2f}s")
        
        # Bottleneck identification
        bottleneck_id = analysis.get('bottleneck_identification', {})
        if bottleneck_id:
            print("\nBOTTLENECK ANALYSIS:")
            print("-" * 50)
            primary = bottleneck_id.get('primary_bottleneck', 'unknown')
            ratio = bottleneck_id.get('fetch_vs_get_ratio', 0)
            fetch_pct = bottleneck_id.get('fetch_percentage', 0)
            
            print(f"Primary Bottleneck: {primary}")
            print(f"Fetch vs Get Ratio: {ratio:.2f}")
            print(f"Fetch Time Percentage: {fetch_pct:.1f}%")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print("\nRECOMMENDATIONS:")
            print("-" * 50)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        
        print("\n" + "="*100)

def main():
    parser = argparse.ArgumentParser(description='Performance Test Runner for Heario News Search')
    parser.add_argument('--base-url', '-u', type=str, default='http://localhost:5000/api', help='API base URL')
    parser.add_argument('--sequential', '-s', type=int, default=3, help='Number of sequential requests')
    parser.add_argument('--concurrent', '-c', type=int, default=3, help='Number of concurrent requests')
    parser.add_argument('--stress-test', action='store_true', help='Run stress test')
    parser.add_argument('--stress-duration', type=int, default=30, help='Stress test duration in seconds')
    parser.add_argument('--stress-rps', type=int, default=1, help='Stress test requests per second')
    parser.add_argument('--queries', nargs='+', default=['台灣', 'AI', '科技'], help='Test queries')
    
    args = parser.parse_args()
    
    test_config = {
        'queries': args.queries,
        'run_sequential': True,
        'sequential_requests': args.sequential,
        'run_concurrent': True,
        'concurrent_requests': args.concurrent,
        'run_stress_test': args.stress_test,
        'stress_duration': args.stress_duration,
        'stress_rps': args.stress_rps
    }
    
    runner = PerformanceTestRunner(base_url=args.base_url)
    runner.run_comprehensive_test(test_config)

if __name__ == '__main__':
    main()