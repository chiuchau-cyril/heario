"""
測試異步優化功能
"""

import asyncio
import time
import os
from jina_performance_optimization import OptimizedJinaFetcher

async def test_async_optimization():
    """測試異步優化效果"""
    
    # 測試 URLs (包含一些問題URL來測試過濾功能)
    test_urls = [
        "https://tw.news.yahoo.com/不只容貌焦慮！8成年輕人患「膚況焦慮症」，毛孔、黑眼圈這8個肌膚問題上榜-005123204.html",
        "https://consent.yahoo.com/v2/collectConsent?sessionId=test",  # 應該被過濾
        "https://tw.news.yahoo.com/藍白用前瞻消費南部-不提雙北坐享千億防洪成果-他嘆-治水不是變魔術-005100071.html",
        "https://www.cna.com.tw/news/aipl/202501040123.aspx",
        "https://privacy-policy.example.com"  # 應該被過濾
    ]
    
    fetcher = OptimizedJinaFetcher(
        jina_api_key=os.getenv('JINA_API_KEY'),
        cache_ttl=3600
    )
    
    print("🚀 測試異步優化效果")
    print("=" * 60)
    
    # 1. 測試並行處理 (ThreadPoolExecutor)
    print("1. 測試並行處理 (ThreadPoolExecutor)...")
    start_time = time.time()
    parallel_results = fetcher.fetch_urls_parallel(
        test_urls, 
        max_workers=5, 
        timeout=6
    )
    parallel_time = time.time() - start_time
    
    parallel_success = sum(1 for content in parallel_results.values() if content)
    print(f"   並行處理完成: {parallel_time:.2f}s")
    print(f"   成功率: {parallel_success}/{len(test_urls)} ({parallel_success/len(test_urls)*100:.1f}%)")
    
    # 2. 測試異步處理 (aiohttp)
    print("\n2. 測試異步處理 (aiohttp)...")
    start_time = time.time()
    async_results = await fetcher.fetch_urls_async(test_urls, timeout=6)
    async_time = time.time() - start_time
    
    async_success = sum(1 for content in async_results.values() if content)
    print(f"   異步處理完成: {async_time:.2f}s")
    print(f"   成功率: {async_success}/{len(test_urls)} ({async_success/len(test_urls)*100:.1f}%)")
    
    # 3. 比較效果
    print("\n" + "=" * 60)
    print("📊 效能比較:")
    print(f"   並行處理: {parallel_time:.2f}s ({parallel_success} 成功)")
    print(f"   異步處理: {async_time:.2f}s ({async_success} 成功)")
    
    if async_time < parallel_time:
        improvement = ((parallel_time - async_time) / parallel_time) * 100
        print(f"   異步處理快 {improvement:.1f}%")
    else:
        improvement = ((async_time - parallel_time) / async_time) * 100
        print(f"   並行處理快 {improvement:.1f}%")
    
    # 4. 測試快取效果
    print("\n3. 測試快取效果...")
    cache_start = time.time()
    cached_results = await fetcher.fetch_urls_async(test_urls[:2], timeout=6)  # 重複請求前兩個URL
    cache_time = time.time() - cache_start
    print(f"   快取測試完成: {cache_time:.2f}s")
    
    if cache_time < 1.0:
        print("   ✅ 快取效果顯著 (< 1秒)")
    else:
        print("   ⚠️  快取效果有限")
    
    # 5. 顯示詳細結果
    print("\n4. 詳細結果:")
    for url, content in async_results.items():
        status = "✅ 成功" if content else "❌ 失敗"
        url_preview = url[:80] + "..." if len(url) > 80 else url
        content_length = len(content) if content else 0
        print(f"   {status} {url_preview} ({content_length} chars)")
    
    print("\n" + "=" * 60)
    print("✅ 異步優化測試完成！")
    
    return {
        'parallel_time': parallel_time,
        'async_time': async_time,
        'parallel_success': parallel_success,
        'async_success': async_success,
        'cache_time': cache_time
    }

if __name__ == "__main__":
    # 載入環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(test_async_optimization())