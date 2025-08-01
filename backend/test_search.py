#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(__file__))

from services.news_crawler import NewsCrawler

def test_search():
    crawler = NewsCrawler()
    
    print("Testing News API search...")
    
    # 測試不同的搜尋關鍵字
    queries = ['Taiwan', '台灣', 'Taiwan OR 台灣', 'China']
    
    for query in queries:
        print(f"\nTesting query: {query}")
        articles = crawler.fetch_news(query=query, language='', page_size=3)
        print(f"Found {len(articles)} articles")
        
        for i, article in enumerate(articles[:2]):
            print(f"  {i+1}. {article.get('title', 'No title')}")
            print(f"     URL: {article.get('url', 'No URL')}")

if __name__ == "__main__":
    test_search()