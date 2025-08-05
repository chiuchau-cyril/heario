"""
Jina AI Performance Optimization Implementation
==============================================
This module implements performance optimizations for Jina AI content fetching
based on the bottleneck analysis results.
"""

import asyncio
import aiohttp
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class OptimizedJinaFetcher:
    """Optimized Jina AI content fetcher with parallel processing and caching"""
    
    def __init__(self, jina_api_key: str = None, cache_ttl: int = 3600):
        self.jina_api_key = jina_api_key
        self.cache = {}
        self.cache_ttl = cache_ttl
        
    def is_blocked_url(self, url: str) -> bool:
        """Quick check for commonly blocked or problematic URLs"""
        blocked_patterns = [
            'consent.yahoo.com',
            'collectConsent',
            'privacy-policy',
            'cookie-policy',
            'terms-of-service'
        ]
        return any(pattern in url.lower() for pattern in blocked_patterns)
    
    def get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return f"jina_cache_{hash(url)}"
    
    def get_cached_content(self, url: str) -> str:
        """Get cached content if available and not expired"""
        cache_key = self.get_cache_key(url)
        if cache_key in self.cache:
            content, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"CACHE_HIT - URL: {url[:100]}...")
                return content
            else:
                # Remove expired cache
                del self.cache[cache_key]
        return None
    
    def cache_content(self, url: str, content: str):
        """Cache content with timestamp"""
        cache_key = self.get_cache_key(url)
        self.cache[cache_key] = (content, time.time())
        logger.info(f"CACHE_STORE - URL: {url[:100]}..., Content Length: {len(content)}")
    
    def fetch_single_url(self, url: str, timeout: int = 10) -> Tuple[str, str, float]:
        """
        Fetch content from a single URL with optimizations
        Returns: (url, content, fetch_time)
        """
        start_time = time.time()
        
        # Quick filter for blocked URLs
        if self.is_blocked_url(url):
            logger.warning(f"BLOCKED_URL_SKIP - URL: {url}")
            return url, "", time.time() - start_time
        
        # Check cache first
        cached = self.get_cached_content(url)
        if cached:
            return url, cached, time.time() - start_time
        
        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            'Accept': 'text/plain',
            'User-Agent': 'Mozilla/5.0 (compatible; Heario/1.0)'
        }
        
        if self.jina_api_key:
            headers['Authorization'] = f'Bearer {self.jina_api_key}'
        
        try:
            response = requests.get(jina_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Check for JSON error response
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    if error_data.get('code') == 451:
                        logger.warning(f"JINA_BLOCKED - URL: {url}, Message: {error_data.get('message', 'Unknown')}")
                        return url, "", time.time() - start_time
                except:
                    pass
            
            content = response.text.strip()
            
            # Basic content validation
            if len(content) < 100:
                logger.warning(f"CONTENT_TOO_SHORT - URL: {url}, Length: {len(content)}")
                return url, "", time.time() - start_time
            
            # Check for invalid content indicators
            invalid_indicators = [
                "blocked until", "ddos attack", "consent.yahoo.com", 
                "collectConsent", "Warning: Target URL", "404 Not Found",
                "Access Denied", "Please enable JavaScript"
            ]
            
            content_lower = content.lower()
            for indicator in invalid_indicators:
                if indicator.lower() in content_lower:
                    logger.warning(f"INVALID_CONTENT - URL: {url}, Indicator: {indicator}")
                    return url, "", time.time() - start_time
            
            # Cache successful result
            self.cache_content(url, content)
            
            fetch_time = time.time() - start_time
            logger.info(f"JINA_SUCCESS_OPTIMIZED - URL: {url[:100]}..., Time: {fetch_time:.2f}s, Content: {len(content)} chars")
            return url, content, fetch_time
            
        except requests.exceptions.Timeout:
            logger.warning(f"JINA_TIMEOUT - URL: {url}, Timeout: {timeout}s")
            return url, "", time.time() - start_time
        except Exception as e:
            logger.error(f"JINA_ERROR - URL: {url}, Error: {str(e)}")
            return url, "", time.time() - start_time
    
    def fetch_urls_parallel(self, urls: List[str], max_workers: int = 5, timeout: int = 10) -> Dict[str, str]:
        """
        Fetch multiple URLs in parallel using ThreadPoolExecutor
        Returns: {url: content} dictionary
        """
        logger.info(f"PARALLEL_FETCH_START - URLs: {len(urls)}, Workers: {max_workers}, Timeout: {timeout}s")
        start_time = time.time()
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all URL fetch tasks
            future_to_url = {
                executor.submit(self.fetch_single_url, url, timeout): url 
                for url in urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    original_url, content, fetch_time = future.result()
                    results[original_url] = content
                except Exception as e:
                    logger.error(f"PARALLEL_FETCH_ERROR - URL: {url}, Error: {str(e)}")
                    results[url] = ""
        
        total_time = time.time() - start_time
        successful = sum(1 for content in results.values() if content)
        
        logger.info(f"PARALLEL_FETCH_COMPLETE - Total: {total_time:.2f}s, Success: {successful}/{len(urls)}")
        return results
    
    async def fetch_urls_async(self, urls: List[str], timeout: int = 10) -> Dict[str, str]:
        """
        Fetch multiple URLs asynchronously using aiohttp
        Returns: {url: content} dictionary
        """
        logger.info(f"ASYNC_FETCH_START - URLs: {len(urls)}, Timeout: {timeout}s")
        start_time = time.time()
        
        async def fetch_single_async(session, url):
            # Quick filter for blocked URLs
            if self.is_blocked_url(url):
                logger.warning(f"ASYNC_BLOCKED_URL_SKIP - URL: {url}")
                return url, ""
            
            # Check cache first
            cached = self.get_cached_content(url)
            if cached:
                return url, cached
            
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                'Accept': 'text/plain',
                'User-Agent': 'Mozilla/5.0 (compatible; Heario/1.0)'
            }
            
            if self.jina_api_key:
                headers['Authorization'] = f'Bearer {self.jina_api_key}'
            
            try:
                async with session.get(jina_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        content = content.strip()
                        
                        if len(content) >= 100:
                            # Cache successful result
                            self.cache_content(url, content)
                            logger.info(f"ASYNC_SUCCESS - URL: {url[:100]}..., Content: {len(content)} chars")
                            return url, content
                    
                    logger.warning(f"ASYNC_ERROR - URL: {url}, Status: {response.status}")
                    return url, ""
                    
            except asyncio.TimeoutError:
                logger.warning(f"ASYNC_TIMEOUT - URL: {url}")
                return url, ""
            except Exception as e:
                logger.error(f"ASYNC_ERROR - URL: {url}, Error: {str(e)}")
                return url, ""
        
        # Create aiohttp session with timeout
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            tasks = [fetch_single_async(session, url) for url in urls]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results to dictionary
        results = {}
        successful = 0
        for result in results_list:
            if isinstance(result, tuple):
                url, content = result
                results[url] = content
                if content:
                    successful += 1
            else:
                logger.error(f"ASYNC_EXCEPTION - {str(result)}")
        
        total_time = time.time() - start_time
        logger.info(f"ASYNC_FETCH_COMPLETE - Total: {total_time:.2f}s, Success: {successful}/{len(urls)}")
        return results


def integrate_optimized_fetcher():
    """
    Integration function to replace the existing fetch_with_jina method
    in NewsCrawler with the optimized version.
    """
    logger.info("Integrating optimized Jina fetcher...")
    
    # This would be used to monkey-patch or replace the existing method
    # in the news crawler for seamless integration
    pass


if __name__ == "__main__":
    # Test the optimized fetcher
    import os
    
    # Test URLs (mix of good and problematic ones)
    test_urls = [
        "https://tw.news.yahoo.com/不只容貌焦慮！8成年輕人患「膚況焦慮症」，毛孔、黑眼圈這8個肌膚問題上榜-005123204.html",
        "https://consent.yahoo.com/v2/collectConsent?sessionId=test",  # This should be skipped
        "https://tw.news.yahoo.com/藍白用前瞻消費南部-不提雙北坐享千億防洪成果-他嘆-治水不是變魔術-005100071.html"
    ]
    
    # Initialize optimized fetcher
    fetcher = OptimizedJinaFetcher(jina_api_key=os.getenv('JINA_API_KEY'))
    
    print("🚀 Testing Optimized Jina Fetcher")
    print("=" * 50)
    
    # Test parallel fetching
    print("Testing parallel fetching...")
    start_time = time.time()
    results = fetcher.fetch_urls_parallel(test_urls, max_workers=3, timeout=8)
    parallel_time = time.time() - start_time
    
    print(f"Parallel fetch completed in {parallel_time:.2f}s")
    successful = sum(1 for content in results.values() if content)
    print(f"Success rate: {successful}/{len(test_urls)} ({successful/len(test_urls)*100:.1f}%)")
    
    for url, content in results.items():
        print(f"  {url[:80]}... -> {len(content)} chars")
    
    print("\n" + "=" * 50)
    print("✅ Optimization test complete!")