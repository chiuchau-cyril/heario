"""
異步新聞處理模組
實作背景處理和即時狀態更新
"""

from flask import Blueprint, jsonify, request, current_app
import asyncio
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any
import logging
from bson import ObjectId

from models.news import NewsItem
from services.news_crawler import NewsCrawler
from services.summarizer import Summarizer
from jina_performance_optimization import OptimizedJinaFetcher
from routes.news import create_smart_summary
import os

async_news_bp = Blueprint('async_news', __name__)
logger = logging.getLogger(__name__)

# 儲存搜尋任務狀態
search_tasks: Dict[str, Dict[str, Any]] = {}

def run_async_in_thread(coro):
    """在新執行緒中執行異步函數"""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_in_thread)
    thread.start()
    return thread

async def async_process_news(task_id: str, query: str, page_size: int = 10, app=None):
    """異步處理新聞搜尋"""
    if app is None:
        from flask import current_app
        app = current_app._get_current_object()
    
    with app.app_context():
        try:
            # 更新狀態：開始搜尋
            search_tasks[task_id].update({
                'status': 'fetching_articles',
                'message': '正在搜尋新聞...',
                'progress': 10
            })
            
            # 1. 抓取新聞文章
            crawler = NewsCrawler()
            articles = crawler.fetch_news(query=query, language='', page_size=page_size)
            
            if not articles:
                search_tasks[task_id].update({
                    'status': 'completed',
                    'message': '沒有找到相關新聞',
                    'progress': 100,
                    'articles': []
                })
                return
            
            # 更新狀態：過濾文章
            search_tasks[task_id].update({
                'status': 'filtering_articles',
                'message': f'找到 {len(articles)} 篇文章，正在過濾...',
                'progress': 30
            })
            
            # 2. 過濾已存在的文章
            db = app.config['db']
            news_collection = db.news
            
            urls_to_process = []
            articles_to_process = []
            
            for article in articles:
                url = article.get('url')
                if not url:
                    continue
                
                existing = news_collection.find_one({'url': url})
                if existing:
                    continue
                    
                urls_to_process.append(url)
                articles_to_process.append(article)
            
            if not urls_to_process:
                # 返回已存在的文章
                existing_articles = []
                for article in articles:
                    if article.get('url'):
                        existing = news_collection.find_one({'url': article['url']})
                        if existing:
                            existing_articles.append(NewsItem.serialize_for_api(existing))
                
                search_tasks[task_id].update({
                    'status': 'completed',
                    'message': f'所有文章都已存在，返回 {len(existing_articles)} 篇',
                    'progress': 100,
                    'articles': existing_articles[:10]  # 限制返回數量
                })
                return
            
            # 更新狀態：抓取內容
            search_tasks[task_id].update({
                'status': 'fetching_content',
                'message': f'正在抓取 {len(urls_to_process)} 篇文章內容...',
                'progress': 50
            })
            
            # 3. 使用異步抓取內容
            fetcher = OptimizedJinaFetcher(
                jina_api_key=os.getenv('JINA_API_KEY'),
                cache_ttl=3600
            )
            
            content_results = await fetcher.fetch_urls_async(urls_to_process, timeout=6)
            
            # 更新狀態：生成摘要
            search_tasks[task_id].update({
                'status': 'generating_summaries',
                'message': '正在生成摘要...',
                'progress': 75
            })
            
            # 4. 批次生成摘要和儲存
            summarizer = Summarizer()
            processed_articles = []
            
            for i, article in enumerate(articles_to_process):
                url = urls_to_process[i]
                full_content = content_results.get(url, '')
                
                # 如果 Jina 失敗，使用 News API 提供的內容
                if not full_content:
                    full_content = article.get('content') or article.get('description', '')
                
                if full_content and len(full_content) > 50:
                    try:
                        # 使用 Gemini 生成摘要
                        summary = summarizer.generate_summary(
                            content=full_content,
                            title=article.get('title', ''),
                            max_length=150
                        )
                    except Exception as e:
                        logger.error(f"Gemini summary failed: {e}")
                        summary = create_smart_summary(full_content, article.get('title', ''), 150)
                    
                    news_item = NewsItem(
                        title=article.get('title'),
                        summary=summary,
                        url=url,
                        source=article.get('source'),
                        original_content=full_content
                    )
                    
                    # 儲存到資料庫
                    news_dict = news_item.to_dict()
                    news_collection.insert_one(news_dict)
                    # 需要添加 _id 供 serialize_for_api 使用
                    news_dict['_id'] = news_dict.get('_id') or ObjectId()
                    processed_articles.append(NewsItem.serialize_for_api(news_dict))
                    
                    # 即時更新進度
                    progress = 75 + (i + 1) / len(articles_to_process) * 20
                    search_tasks[task_id].update({
                        'progress': int(progress),
                        'message': f'已處理 {i + 1}/{len(articles_to_process)} 篇文章'
                    })
            
            # 完成
            search_tasks[task_id].update({
                'status': 'completed',
                'message': f'成功處理 {len(processed_articles)} 篇新文章',
                'progress': 100,
                'articles': processed_articles,
                'total_processed': len(processed_articles),
                'total_found': len(articles)
            })
            
        except Exception as e:
            logger.error(f"Async news processing failed: {e}")
            search_tasks[task_id].update({
                'status': 'error',
                'message': f'處理失敗: {str(e)}',
                'progress': 100,
                'error': str(e)
            })

@async_news_bp.route('/news/search/async', methods=['POST'])
def start_async_search():
    """開始異步搜尋"""
    try:
        query = request.json.get('query', '台灣')
        page_size = request.json.get('page_size', 10)
        
        # 生成任務ID
        task_id = str(uuid.uuid4())
        
        # 初始化任務狀態
        search_tasks[task_id] = {
            'task_id': task_id,
            'query': query,
            'status': 'started',
            'message': '正在初始化搜尋...',
            'progress': 0,
            'started_at': datetime.now().isoformat(),
            'articles': []
        }
        
        # 在背景執行緒中開始異步處理
        run_async_in_thread(async_process_news(task_id, query, page_size, current_app._get_current_object()))
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': f'開始搜尋「{query}」相關新聞',
            'check_url': f'/api/news/search/status/{task_id}'
        }), 202
        
    except Exception as e:
        logger.error(f"Failed to start async search: {e}")
        return jsonify({'error': str(e)}), 500

@async_news_bp.route('/news/search/status/<task_id>', methods=['GET'])
def get_search_status(task_id: str):
    """獲取搜尋狀態"""
    if task_id not in search_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = search_tasks[task_id]
    
    # 如果任務完成，返回完整結果
    if task['status'] in ['completed', 'error']:
        # 清理舊任務（可選）
        # del search_tasks[task_id]
        pass
    
    return jsonify(task), 200

@async_news_bp.route('/news/search/paginated', methods=['POST'])
def paginated_search():
    """分頁搜尋 - 先返回部分結果，其餘背景處理"""
    try:
        query = request.json.get('query', '台灣')
        page = request.json.get('page', 1)
        per_page = request.json.get('per_page', 5)
        
        db = current_app.config['db']
        news_collection = db.news
        
        # 1. 先快速返回現有的相關新聞
        existing_news = news_collection.find({
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'summary': {'$regex': query, '$options': 'i'}}
            ]
        }).sort('created_at', -1).limit(per_page)
        
        existing_articles = [NewsItem.serialize_for_api(item) for item in existing_news]
        
        # 2. 如果現有新聞不足，啟動背景搜尋
        background_task_id = None
        if len(existing_articles) < per_page:
            # 啟動背景搜尋任務
            task_id = str(uuid.uuid4())
            search_tasks[task_id] = {
                'task_id': task_id,
                'query': query,
                'status': 'started',
                'message': '正在背景搜尋更多新聞...',
                'progress': 0,
                'started_at': datetime.now().isoformat(),
                'articles': []
            }
            
            # 在背景執行
            run_async_in_thread(async_process_news(task_id, query, 10, current_app._get_current_object()))
            background_task_id = task_id
        
        return jsonify({
            'articles': existing_articles,
            'page': page,
            'per_page': per_page,
            'total_immediate': len(existing_articles),
            'background_task_id': background_task_id,
            'message': f'立即返回 {len(existing_articles)} 篇相關新聞' + (
                '，正在背景搜尋更多新聞' if background_task_id else ''
            )
        }), 200
        
    except Exception as e:
        logger.error(f"Paginated search failed: {e}")
        return jsonify({'error': str(e)}), 500

@async_news_bp.route('/news/search/tasks', methods=['GET'])
def list_search_tasks():
    """列出所有搜尋任務"""
    tasks = []
    for task_id, task in search_tasks.items():
        tasks.append({
            'task_id': task_id,
            'query': task.get('query'),
            'status': task.get('status'),
            'progress': task.get('progress'),
            'message': task.get('message'),
            'started_at': task.get('started_at')
        })
    
    return jsonify({
        'tasks': tasks,
        'total': len(tasks)
    }), 200

@async_news_bp.route('/news/search/tasks/<task_id>', methods=['DELETE'])
def cancel_search_task(task_id: str):
    """取消搜尋任務"""
    if task_id in search_tasks:
        search_tasks[task_id]['status'] = 'cancelled'
        search_tasks[task_id]['message'] = '任務已取消'
        return jsonify({'message': '任務已取消'}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404