"""
測試智能搜尋API
"""

import requests
import time
import json

def test_smart_search():
    """測試智能搜尋功能"""
    
    base_url = "http://localhost:5001/api"
    
    print("🔍 測試智能搜尋API")
    print("=" * 50)
    
    # 1. 測試分頁搜尋 (立即回應)
    print("1. 測試分頁搜尋...")
    
    try:
        response = requests.post(f"{base_url}/news/search/paginated", 
                               json={
                                   "query": "泰國,柬埔寨",
                                   "page": 1,
                                   "per_page": 5
                               })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 分頁搜尋成功")
            print(f"   立即結果: {len(data.get('articles', []))} 篇")
            print(f"   訊息: {data.get('message', '')}")
            
            background_task_id = data.get('background_task_id')
            if background_task_id:
                print(f"   背景任務ID: {background_task_id}")
                
                # 2. 監控背景任務
                print("\n2. 監控背景任務...")
                for i in range(10):  # 最多等待10次
                    time.sleep(2)
                    
                    status_response = requests.get(f"{base_url}/news/search/status/{background_task_id}")
                    
                    if status_response.status_code == 200:
                        task_data = status_response.json()
                        status = task_data.get('status')
                        progress = task_data.get('progress', 0)
                        message = task_data.get('message', '')
                        
                        print(f"   進度 {i+1}: {status} ({progress}%) - {message}")
                        
                        if status in ['completed', 'error']:
                            if status == 'completed':
                                articles = task_data.get('articles', [])
                                print(f"   ✅ 背景搜尋完成，新增 {len(articles)} 篇文章")
                            else:
                                error = task_data.get('error', '')
                                print(f"   ❌ 背景搜尋失敗: {error}")
                            break
                    else:
                        print(f"   ❌ 無法獲取任務狀態: {status_response.status_code}")
                        break
            else:
                print("   沒有背景任務 (已有足夠結果)")
                
        else:
            print(f"   ❌ 分頁搜尋失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 請求失敗: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ 智能搜尋API測試完成！")

if __name__ == "__main__":
    print("請確保Flask服務器正在運行 (python app.py)")
    print("按Enter開始測試...")
    input()
    
    test_smart_search()