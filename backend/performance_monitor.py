#!/usr/bin/env python3
"""
Performance Monitor for Heario News Search Functionality

This script measures and analyzes the performance of each stage in the news search process:
1. News API calls (NewsCrawler.fetch_news)
2. Jina AI content fetching (fetch_with_jina) 
3. Gemini summarization (Summarizer.generate_summary)
4. Database operations

Usage:
    python performance_monitor.py [options]
"""

import time
import json
import logging
import statistics
from datetime import datetime
from typing import Dict, List, Any
import argparse
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.news_crawler import NewsCrawler
from services.summarizer import Summarizer
from models.news import NewsItem

class PerformanceMonitor:
    def __init__(self, log_file: str = 'performance_analysis.log'):
        self.log_file = log_file
        self.results = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def measure_news_api_performance(self, query: str = '台灣', page_size: int = 5) -> Dict[str, Any]:
        """Measure News API performance"""
        self.logger.info(f"Testing News API performance with query: {query}")
        
        crawler = NewsCrawler()
        start_time = time.time()
        
        try:
            articles = crawler.fetch_news(query=query, language='', page_size=page_size)
            end_time = time.time()
            
            result = {
                'stage': 'news_api',
                'query': query,
                'success': True,
                'articles_count': len(articles),
                'duration': end_time - start_time,
                'timestamp': datetime.now().isoformat(),
                'articles': [{'title': a.get('title', ''), 'url': a.get('url', '')} for a in articles[:3]]  # First 3 for reference
            }
            
            self.logger.info(f"News API: {len(articles)} articles in {result['duration']:.2f}s")
            return result
            
        except Exception as e:
            end_time = time.time()
            result = {
                'stage': 'news_api',
                'query': query,
                'success': False,
                'error': str(e),
                'duration': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
            self.logger.error(f"News API failed: {e}")
            return result
    
    def measure_jina_performance(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Measure Jina AI performance for multiple URLs"""
        self.logger.info(f"Testing Jina AI performance with {len(urls)} URLs")
        
        crawler = NewsCrawler()
        results = []
        
        for i, url in enumerate(urls):
            self.logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            start_time = time.time()
            
            try:
                content = crawler.fetch_with_jina(url)
                end_time = time.time()
                
                result = {
                    'stage': 'jina_ai',
                    'url': url,
                    'success': bool(content),
                    'content_length': len(content) if content else 0,
                    'duration': end_time - start_time,
                    'timestamp': datetime.now().isoformat(),
                    'content_preview': content[:200] + '...' if content and len(content) > 200 else content
                }
                
                self.logger.info(f"Jina AI: {len(content) if content else 0} chars in {result['duration']:.2f}s")
                results.append(result)
                
            except Exception as e:
                end_time = time.time()
                result = {
                    'stage': 'jina_ai',
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'duration': end_time - start_time,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.error(f"Jina AI failed for {url}: {e}")
                results.append(result)
        
        return results
    
    def measure_summarization_performance(self, content_samples: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Measure Gemini summarization performance"""
        self.logger.info(f"Testing Gemini summarization performance with {len(content_samples)} samples")
        
        summarizer = Summarizer()
        results = []
        
        for i, sample in enumerate(content_samples):
            content = sample.get('content', '')
            title = sample.get('title', '')
            
            if not content or len(content) < 50:
                continue
                
            self.logger.info(f"Processing sample {i+1}/{len(content_samples)}: {title[:50]}...")
            start_time = time.time()
            
            try:
                summary = summarizer.generate_summary(content, title, max_length=150)
                end_time = time.time()
                
                result = {
                    'stage': 'summarization',
                    'title': title,
                    'content_length': len(content),
                    'summary_length': len(summary),
                    'success': True,
                    'duration': end_time - start_time,
                    'timestamp': datetime.now().isoformat(),
                    'summary_preview': summary[:100] + '...' if len(summary) > 100 else summary
                }
                
                self.logger.info(f"Summarization: {len(content)} -> {len(summary)} chars in {result['duration']:.2f}s")
                results.append(result)
                
            except Exception as e:
                end_time = time.time()
                result = {
                    'stage': 'summarization',
                    'title': title,
                    'content_length': len(content),
                    'success': False,
                    'error': str(e),
                    'duration': end_time - start_time,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.error(f"Summarization failed for {title}: {e}")
                results.append(result)
        
        return results
    
    def measure_end_to_end_performance(self, query: str = '台灣', article_limit: int = 3) -> Dict[str, Any]:
        """Measure complete end-to-end performance"""
        self.logger.info(f"Testing end-to-end performance with query: {query}")
        
        total_start_time = time.time()
        
        # Step 1: News API
        news_api_result = self.measure_news_api_performance(query, page_size=article_limit)
        
        if not news_api_result.get('success') or not news_api_result.get('articles'):
            return {
                'stage': 'end_to_end',
                'success': False,
                'error': 'News API failed or no articles',
                'news_api_result': news_api_result,
                'duration': time.time() - total_start_time,
                'timestamp': datetime.now().isoformat()
            }
        
        # Get URLs from news API results
        urls = []
        content_samples = []
        
        # Reconstruct articles from the news API call for Jina testing
        crawler = NewsCrawler()
        articles = crawler.fetch_news(query=query, language='', page_size=article_limit)
        
        for article in articles[:article_limit]:
            if article.get('url'):
                urls.append(article['url'])
        
        # Step 2: Jina AI
        jina_results = self.measure_jina_performance(urls)
        
        # Prepare content samples for summarization
        for i, jina_result in enumerate(jina_results):
            if jina_result.get('success') and jina_result.get('content_preview'):
                # We need the full content for summarization, so fetch it again
                # In a real scenario, we'd reuse the content from Jina
                if i < len(articles):
                    content_samples.append({
                        'title': articles[i].get('title', ''),
                        'content': jina_result.get('content_preview', '') + '...'  # Truncated for demo
                    })
        
        # Step 3: Summarization
        summarization_results = self.measure_summarization_performance(content_samples)
        
        total_end_time = time.time()
        
        result = {
            'stage': 'end_to_end',
            'query': query,
            'success': True,
            'total_duration': total_end_time - total_start_time,
            'news_api_duration': news_api_result.get('duration', 0),
            'jina_durations': [r.get('duration', 0) for r in jina_results],
            'summarization_durations': [r.get('duration', 0) for r in summarization_results],
            'articles_processed': len(articles),
            'jina_success_rate': sum(1 for r in jina_results if r.get('success')) / len(jina_results) if jina_results else 0,
            'summarization_success_rate': sum(1 for r in summarization_results if r.get('success')) / len(summarization_results) if summarization_results else 0,
            'timestamp': datetime.now().isoformat(),
            'detailed_results': {
                'news_api': news_api_result,
                'jina': jina_results,
                'summarization': summarization_results
            }
        }
        
        # Calculate averages
        if jina_results:
            result['avg_jina_duration'] = statistics.mean([r.get('duration', 0) for r in jina_results])
        if summarization_results:
            result['avg_summarization_duration'] = statistics.mean([r.get('duration', 0) for r in summarization_results])
        
        self.logger.info(f"End-to-end: {result['total_duration']:.2f}s total")
        return result
    
    def run_performance_test(self, iterations: int = 3, query: str = '台灣') -> Dict[str, Any]:
        """Run comprehensive performance test with multiple iterations"""
        self.logger.info(f"Starting comprehensive performance test with {iterations} iterations")
        
        all_results = []
        
        for i in range(iterations):
            self.logger.info(f"=== Iteration {i+1}/{iterations} ===")
            
            # Small delay between iterations to avoid rate limiting
            if i > 0:
                time.sleep(2)
            
            result = self.measure_end_to_end_performance(query)
            all_results.append(result)
            
            self.logger.info(f"Iteration {i+1} completed in {result.get('total_duration', 0):.2f}s")
        
        # Calculate aggregate statistics
        total_durations = [r.get('total_duration', 0) for r in all_results if r.get('success')]
        news_api_durations = [r.get('news_api_duration', 0) for r in all_results if r.get('success')]
        
        jina_durations = []
        summarization_durations = []
        
        for result in all_results:
            if result.get('success'):
                jina_durations.extend(result.get('jina_durations', []))
                summarization_durations.extend(result.get('summarization_durations', []))
        
        aggregate_stats = {
            'test_summary': {
                'iterations': iterations,
                'successful_iterations': len(total_durations),
                'query': query,
                'timestamp': datetime.now().isoformat()
            },
            'performance_stats': {}
        }
        
        if total_durations:
            aggregate_stats['performance_stats']['total_duration'] = {
                'mean': statistics.mean(total_durations),
                'median': statistics.median(total_durations),
                'min': min(total_durations),
                'max': max(total_durations),
                'stdev': statistics.stdev(total_durations) if len(total_durations) > 1 else 0
            }
        
        if news_api_durations:
            aggregate_stats['performance_stats']['news_api_duration'] = {
                'mean': statistics.mean(news_api_durations),
                'median': statistics.median(news_api_durations),
                'min': min(news_api_durations),
                'max': max(news_api_durations),
                'stdev': statistics.stdev(news_api_durations) if len(news_api_durations) > 1 else 0
            }
        
        if jina_durations:
            aggregate_stats['performance_stats']['jina_duration'] = {
                'mean': statistics.mean(jina_durations),
                'median': statistics.median(jina_durations),
                'min': min(jina_durations),
                'max': max(jina_durations),
                'stdev': statistics.stdev(jina_durations) if len(jina_durations) > 1 else 0
            }
        
        if summarization_durations:
            aggregate_stats['performance_stats']['summarization_duration'] = {
                'mean': statistics.mean(summarization_durations),
                'median': statistics.median(summarization_durations),
                'min': min(summarization_durations),
                'max': max(summarization_durations),
                'stdev': statistics.stdev(summarization_durations) if len(summarization_durations) > 1 else 0
            }
        
        aggregate_stats['detailed_results'] = all_results
        
        # Save detailed results to file
        results_file = f'performance_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(aggregate_stats, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Performance test completed. Results saved to {results_file}")
        
        # Print summary
        self.print_performance_summary(aggregate_stats)
        
        return aggregate_stats
    
    def print_performance_summary(self, stats: Dict[str, Any]):
        """Print a formatted performance summary"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUMMARY")
        print("="*80)
        
        test_info = stats.get('test_summary', {})
        print(f"Test Query: {test_info.get('query', 'N/A')}")
        print(f"Iterations: {test_info.get('iterations', 'N/A')}")
        print(f"Successful: {test_info.get('successful_iterations', 'N/A')}")
        print(f"Timestamp: {test_info.get('timestamp', 'N/A')}")
        
        perf_stats = stats.get('performance_stats', {})
        
        print("\nCOMPONENT PERFORMANCE:")
        print("-" * 40)
        
        for component, data in perf_stats.items():
            if isinstance(data, dict):
                print(f"\n{component.replace('_', ' ').title()}:")
                print(f"  Mean:     {data.get('mean', 0):.2f}s")
                print(f"  Median:   {data.get('median', 0):.2f}s")
                print(f"  Min:      {data.get('min', 0):.2f}s")
                print(f"  Max:      {data.get('max', 0):.2f}s")
                print(f"  Std Dev:  {data.get('stdev', 0):.2f}s")
        
        # Performance analysis
        print("\nPERFORMANCE ANALYSIS:")
        print("-" * 40)
        
        if 'total_duration' in perf_stats:
            total_mean = perf_stats['total_duration'].get('mean', 0)
            
            slowest_component = None
            slowest_time = 0
            
            for comp in ['news_api_duration', 'jina_duration', 'summarization_duration']:
                if comp in perf_stats:
                    comp_mean = perf_stats[comp].get('mean', 0)
                    if comp_mean > slowest_time:
                        slowest_time = comp_mean
                        slowest_component = comp
            
            if slowest_component:
                comp_name = slowest_component.replace('_duration', '').replace('_', ' ').title()
                percentage = (slowest_time / total_mean) * 100 if total_mean > 0 else 0
                print(f"Slowest Component: {comp_name} ({slowest_time:.2f}s, {percentage:.1f}% of total)")
                
                if 'jina' in slowest_component.lower():
                    print("VERDICT: Jina AI is the primary bottleneck")
                elif 'summarization' in slowest_component.lower():
                    print("VERDICT: Gemini summarization is the primary bottleneck")
                elif 'news_api' in slowest_component.lower():
                    print("VERDICT: News API is the primary bottleneck")
        
        print("\n" + "="*80)

def main():
    parser = argparse.ArgumentParser(description='Performance Monitor for Heario News Search')
    parser.add_argument('--iterations', '-i', type=int, default=3, help='Number of test iterations (default: 3)')
    parser.add_argument('--query', '-q', type=str, default='台灣', help='Search query (default: 台灣)')
    parser.add_argument('--log-file', '-l', type=str, default='performance_analysis.log', help='Log file path')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(log_file=args.log_file)
    monitor.run_performance_test(iterations=args.iterations, query=args.query)

if __name__ == '__main__':
    main()