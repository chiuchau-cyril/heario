#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(__file__))

from services.news_crawler import NewsCrawler
from services.summarizer import Summarizer
from routes.news import create_smart_summary
from dotenv import load_dotenv

load_dotenv()

def test_single_news():
    """測試單筆新聞的完整處理流程"""
    try:
        crawler = NewsCrawler()
        summarizer = Summarizer()
        
        print("=== 步驟 1: 獲取 News API 資料 ===")
        articles = crawler.fetch_news(query='Taiwan', language='', page_size=1)
        
        if not articles:
            print("❌ 沒有找到新聞")
            return
        
        article = articles[0]
        print(f"✅ 找到新聞: {article.get('title')}")
        print(f"📰 原始 URL: {article.get('url')}")
        print(f"📝 News API description: {article.get('description', '')[:100]}...")
        
        print("\n=== 步驟 2: 使用 Jina AI 抓取完整內容 ===")
        jina_content = crawler.fetch_with_jina(article.get('url'))
        
        if jina_content:
            print(f"✅ Jina AI 成功獲取內容，長度: {len(jina_content)} 字元")
            print(f"📖 Jina 內容預覽:")
            print("=" * 50)
            print(jina_content[:500] + "..." if len(jina_content) > 500 else jina_content)
            print("=" * 50)
        else:
            print("❌ Jina AI 獲取失敗，使用 News API 內容")
            jina_content = article.get('content') or article.get('description', '')
            print(f"📝 News API 內容: {jina_content[:200]}...")
        
        print(f"\n=== 步驟 3: 使用 OpenAI 生成摘要 ===")
        if len(jina_content) > 50:
            try:
                summary = summarizer.generate_summary(
                    content=jina_content,
                    title=article.get('title', ''),
                    max_length=200
                )
                print(f"✅ OpenAI 摘要成功:")
                print(f"📋 {summary}")
            except Exception as e:
                print(f"❌ OpenAI 摘要失敗: {e}")
                summary = create_smart_summary(jina_content, article.get('title', ''), 200)
                print(f"🧠 使用智能摘要:")
                print(f"📋 {summary}")
        else:
            summary = f"{article.get('title')} - 詳細內容請點擊原文連結查看。"
            print(f"⚠️  內容太短，使用預設摘要: {summary}")
        
        print(f"\n=== 處理結果摘要 ===")
        print(f"🔗 處理鏈: News API -> Jina AI -> OpenAI/智能摘要")
        print(f"📊 原始描述長度: {len(article.get('description', ''))}")
        print(f"📊 Jina 內容長度: {len(jina_content)}")
        print(f"📊 最終摘要長度: {len(summary)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_news()