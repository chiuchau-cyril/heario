#!/usr/bin/env python3
"""
Quick Performance Test Script for Heario

This script runs a fast performance test to quickly identify if Jina AI is the bottleneck.
"""

import time
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.news_crawler import NewsCrawler
from services.summarizer import Summarizer

def quick_test():
    print("🔍 Quick Performance Test for Heario News Search")
    print("=" * 60)
    
    # Initialize services
    crawler = NewsCrawler()
    summarizer = Summarizer()
    
    print("1. Testing News API...")
    news_start = time.time()
    try:
        articles = crawler.fetch_news(query='台灣', page_size=3)
        news_time = time.time() - news_start
        print(f"   ✅ News API: {len(articles)} articles in {news_time:.2f}s")
        
        if not articles:
            print("   ❌ No articles found. Check NEWS_API_KEY.")
            return
        
    except Exception as e:
        print(f"   ❌ News API failed: {e}")
        return
    
    print("\n2. Testing Jina AI (processing 2 articles)...")
    jina_times = []
    jina_successes = 0
    
    for i, article in enumerate(articles[:2]):
        url = article.get('url', '')
        if not url:
            continue
            
        print(f"   Processing article {i+1}: {article.get('title', 'Unknown')[:50]}...")
        
        jina_start = time.time()
        try:
            content = crawler.fetch_with_jina(url)
            jina_time = time.time() - jina_start
            jina_times.append(jina_time)
            
            if content and len(content) > 100:
                jina_successes += 1
                print(f"   ✅ Jina AI: {len(content)} chars in {jina_time:.2f}s")
            else:
                print(f"   ⚠️  Jina AI: No content or too short ({len(content) if content else 0} chars) in {jina_time:.2f}s")
                
        except Exception as e:
            jina_time = time.time() - jina_start
            jina_times.append(jina_time)
            print(f"   ❌ Jina AI failed in {jina_time:.2f}s: {e}")
    
    avg_jina_time = sum(jina_times) / len(jina_times) if jina_times else 0
    jina_success_rate = jina_successes / len(jina_times) if jina_times else 0
    
    print(f"\n   📊 Jina AI Summary: {avg_jina_time:.2f}s average, {jina_success_rate:.1%} success rate")
    
    print("\n3. Testing Gemini Summarization...")
    if jina_successes > 0:
        # Use the first successful Jina result for summarization
        test_content = None
        test_title = ""
        
        for i, article in enumerate(articles[:2]):
            url = article.get('url', '')
            if url:
                content = crawler.fetch_with_jina(url)
                if content and len(content) > 100:
                    test_content = content
                    test_title = article.get('title', '')
                    break
        
        if test_content:
            summarization_start = time.time()
            try:
                summary = summarizer.generate_summary(test_content, test_title, max_length=150)
                summarization_time = time.time() - summarization_start
                print(f"   ✅ Gemini: {len(summary)} chars summary in {summarization_time:.2f}s")
                print(f"   📝 Summary preview: {summary[:100]}...")
            except Exception as e:
                summarization_time = time.time() - summarization_start
                print(f"   ❌ Gemini failed in {summarization_time:.2f}s: {e}")
        else:
            summarization_time = 0
            print("   ⚠️  No content available for summarization testing")
    else:
        summarization_time = 0
        print("   ⚠️  Skipping summarization (no successful Jina results)")
    
    # Analysis
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    total_estimated_time = news_time + (avg_jina_time * 3) + (summarization_time * 3)  # Estimate for 3 articles
    
    print(f"News API Time:          {news_time:.2f}s ({news_time/total_estimated_time*100:.1f}%)")
    print(f"Avg Jina AI Time:       {avg_jina_time:.2f}s per article ({avg_jina_time*3/total_estimated_time*100:.1f}% for 3 articles)")
    print(f"Summarization Time:     {summarization_time:.2f}s per article ({summarization_time*3/total_estimated_time*100:.1f}% for 3 articles)")
    print(f"Estimated Total Time:   {total_estimated_time:.2f}s for 3 articles")
    
    # Bottleneck identification
    print("\n🎯 BOTTLENECK ANALYSIS:")
    
    components = [
        ("News API", news_time),
        ("Jina AI (per article)", avg_jina_time),
        ("Summarization (per article)", summarization_time)
    ]
    
    # Find slowest component
    slowest_component = max(components, key=lambda x: x[1])
    
    if slowest_component[1] > 0:
        print(f"Primary bottleneck: {slowest_component[0]} ({slowest_component[1]:.2f}s)")
        
        if "Jina AI" in slowest_component[0]:
            print("\n🔧 RECOMMENDATIONS FOR JINA AI BOTTLENECK:")
            print("   • Reduce Jina AI timeout from 30s to 15s")
            print("   • Implement parallel processing for multiple articles")
            print("   • Add caching for frequently accessed URLs")
            print("   • Consider using fallback content sources")
            
            if jina_success_rate < 0.8:
                print("   • Low success rate - check blocked domains or API limits")
        
        elif "Summarization" in slowest_component[0]:
            print("\n🔧 RECOMMENDATIONS FOR SUMMARIZATION BOTTLENECK:")
            print("   • Implement request batching for Gemini API")
            print("   • Reduce content size before summarization")
            print("   • Add caching for similar content")
            print("   • Consider using faster summarization models")
        
        elif "News API" in slowest_component[0]:
            print("\n🔧 RECOMMENDATIONS FOR NEWS API BOTTLENECK:")
            print("   • Check network connectivity")
            print("   • Verify API key and rate limits")
            print("   • Consider using different news sources")
    
    # Overall recommendations
    print("\n💡 GENERAL RECOMMENDATIONS:")
    if total_estimated_time > 30:
        print("   • Total time is very high (>30s) - urgent optimization needed")
    elif total_estimated_time > 15:
        print("   • Total time is high (>15s) - optimization recommended")
    
    if jina_success_rate < 0.9:
        print(f"   • Jina AI success rate is low ({jina_success_rate:.1%}) - investigate blocked domains")
    
    print("\n📋 NEXT STEPS:")
    print("   1. Run full performance analysis: python performance_monitor.py")
    print("   2. Run load testing: python performance_test_runner.py")
    print("   3. Monitor real-time performance at: http://localhost:5001/api/performance/dashboard")

if __name__ == '__main__':
    quick_test()