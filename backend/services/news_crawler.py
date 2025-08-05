import os
import requests
from datetime import datetime, timedelta
import feedparser
from typing import List, Dict
import time
import logging

# Configure performance logging for NewsCrawler
crawler_logger = logging.getLogger('crawler_performance')
crawler_logger.setLevel(logging.INFO)
if not crawler_logger.handlers:
    handler = logging.FileHandler('/Users/cyril/Documents/git/heario/backend/crawler_performance.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    crawler_logger.addHandler(handler)

class NewsCrawler:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.jina_api_key = os.getenv('JINA_API_KEY')
        if not self.news_api_key:
            print("WARNING: NEWS_API_KEY is not set in environment variables")
        
    def fetch_news(self, query='台灣', language='zh', page_size=10) -> List[Dict]:
        """使用 News API 抓取新聞"""
        start_time = time.time()
        base_url = 'https://newsapi.org/v2/everything'
        
        # 擴大時間範圍到過去一週
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': last_week,
            'to': today,
            'sortBy': 'publishedAt',
            'pageSize': page_size,
            'apiKey': self.news_api_key
        }
        
        # 只有在 language 不為空時才加入參數
        if language:
            params['language'] = language
        
        try:
            request_start = time.time()
            response = requests.get(base_url, params=params)
            request_time = time.time() - request_start
            response.raise_for_status()
            data = response.json()
            
            total_time = time.time() - start_time
            articles_count = len(data.get('articles', []))
            
            crawler_logger.info(f"NEWS_API_FETCH - Query: {query}, Articles: {articles_count}, Request Time: {request_time:.2f}s, Total Time: {total_time:.2f}s")
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'description': article.get('description'),
                    'content': article.get('content'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt')
                })
            
            return articles
        except Exception as e:
            total_time = time.time() - start_time
            crawler_logger.error(f"NEWS_API_ERROR - Query: {query}, Time: {total_time:.2f}s, Error: {str(e)}")
            print(f"Error fetching News API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return []
    
    def fetch_top_headlines(self, country='tw', category=None, page_size=10) -> List[Dict]:
        """使用 News API 抓取熱門頭條新聞"""
        base_url = 'https://newsapi.org/v2/top-headlines'
        
        params = {
            'country': country,
            'pageSize': page_size,
            'apiKey': self.news_api_key
        }
        
        if category:
            params['category'] = category
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'description': article.get('description'),
                    'content': article.get('content'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt')
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching top headlines: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return []
    
    def fetch_with_jina(self, url: str) -> str:
        """使用 Jina.ai 抓取網頁完整內容"""
        start_time = time.time()
        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            'Accept': 'text/plain',
            'User-Agent': 'Mozilla/5.0 (compatible; Heario/1.0)'
        }
        
        # 如果有 Jina API key，使用認證
        if self.jina_api_key:
            headers['Authorization'] = f'Bearer {self.jina_api_key}'
        
        try:
            request_start = time.time()
            response = requests.get(jina_url, headers=headers, timeout=10)
            request_time = time.time() - request_start
            response.raise_for_status()
            
            # 檢查是否是 JSON 錯誤回應
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    if error_data.get('code') == 451:  # 網站被封鎖
                        total_time = time.time() - start_time
                        crawler_logger.warning(f"JINA_BLOCKED - URL: {url}, Time: {total_time:.2f}s, Message: {error_data.get('message', 'Unknown error')}")
                        print(f"Domain blocked by Jina: {error_data.get('message', 'Unknown error')}")
                        return ""
                except:
                    pass
            
            # Jina 直接回傳文字內容
            content = response.text.strip()
            total_time = time.time() - start_time
            
            # 過濾太短的內容或錯誤內容
            if len(content) < 100:
                crawler_logger.warning(f"JINA_SHORT_CONTENT - URL: {url}, Time: {total_time:.2f}s, Length: {len(content)}")
                print(f"Content too short from Jina: {len(content)} chars")
                return ""
            
            # 檢查是否包含錯誤訊息或無效內容
            invalid_indicators = [
                "blocked until", "ddos attack", "consent.yahoo.com", 
                "collectConsent", "Warning: Target URL", "404 Not Found",
                "Access Denied", "Please enable JavaScript"
            ]
            
            content_lower = content.lower()
            for indicator in invalid_indicators:
                if indicator.lower() in content_lower:
                    crawler_logger.warning(f"JINA_INVALID_CONTENT - URL: {url}, Time: {total_time:.2f}s, Indicator: {indicator}")
                    print(f"Invalid content detected: {indicator}")
                    return ""
            
            # 檢查是否主要是 Yahoo 首頁內容而非新聞內容（更寬鬆的檢查）
            if "yahoo奇摩" in content.lower() and "新聞" not in content and len(content) < 500:
                crawler_logger.warning(f"JINA_YAHOO_HOMEPAGE - URL: {url}, Time: {total_time:.2f}s")
                print("Content appears to be Yahoo homepage, not article content")
                return ""
            
            crawler_logger.info(f"JINA_SUCCESS - URL: {url}, Request Time: {request_time:.2f}s, Total Time: {total_time:.2f}s, Content Length: {len(content)}")
            return content
        except Exception as e:
            total_time = time.time() - start_time
            crawler_logger.error(f"JINA_ERROR - URL: {url}, Time: {total_time:.2f}s, Error: {str(e)}")
            print(f"Error fetching with Jina: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text[:200]}...")
            return ""
    
    def fetch_rss_feed(self, feed_url: str) -> List[Dict]:
        """抓取 RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.get('title'),
                    'url': entry.get('link'),
                    'description': entry.get('summary'),
                    'published_at': entry.get('published')
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []