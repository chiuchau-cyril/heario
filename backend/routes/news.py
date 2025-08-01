from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from bson import ObjectId

from models.news import NewsItem
from services.news_crawler import NewsCrawler
from services.summarizer import Summarizer
import re

news_bp = Blueprint('news', __name__)

def extract_main_content(content: str) -> str:
    """從 Jina AI 回應中提取主要新聞內容"""
    lines = content.split('\n')
    content_lines = []
    content_started = False
    
    # 先找到 "Markdown Content:" 後的實際內容
    for i, line in enumerate(lines):
        line = line.strip()
        if 'Markdown Content:' in line:
            # 從下一行開始提取內容
            for j in range(i + 1, len(lines)):
                content_line = lines[j].strip()
                if not content_line:
                    continue
                    
                # 跳過網站導航和無關元素
                skip_patterns = [
                    '首頁', '新聞', '股市', '運動', 'TV', '汽機車', '購物中心', '拍賣',
                    '登入', '搜尋', 'Yahoo', 'App', '熱搜', '立即下載', '廣告', '訂閱',
                    '隱私權', 'Privacy', 'Cookie', 'Terms', '===', '---', '===============',
                    '*', '[', ']', 'Image', 'href', 'http', 'www.'
                ]
                
                # 檢查是否應該跳過此行
                should_skip = False
                for pattern in skip_patterns:
                    if pattern in content_line:
                        should_skip = True
                        break
                
                # 跳過過短或主要是符號的行
                if len(content_line) < 15 or content_line.startswith(('*', '[', '!')):
                    should_skip = True
                
                # 跳過純英文的導航行
                if re.match(r'^[a-zA-Z\s\d\.,;&%\(\)\[\]]+$', content_line) and len(content_line) > 20:
                    should_skip = True
                
                if not should_skip and len(content_line) > 10:
                    content_lines.append(content_line)
                    
                # 找到足夠的內容就停止
                if len(' '.join(content_lines)) > 1000:
                    break
            break
    
    return ' '.join(content_lines)

def create_smart_summary(content: str, title: str, max_length: int = 150) -> str:
    """創建智能摘要的備用方案"""
    try:
        # 首先提取主要內容
        main_content = extract_main_content(content)
        
        # 如果沒有找到主要內容，回退到簡單清理
        if len(main_content) < 50:
            # 清理內容，移除 Jina 的元數據
            lines = content.split('\n')
            cleaned_lines = []
            
            skip_patterns = [
                'Title:', 'URL Source:', 'Markdown Content:', 'Published Time:',
                '===', '---', 'Warning:', 'collectConsent', 'Yahoo奇摩',
                'Your Privacy Choices', 'If you are a resident of', 'Privacy Policy',
                'Cookie Policy', 'Terms of Service', 'Subscribe', 'Newsletter'
            ]
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 跳過包含特定模式的行
                if any(pattern in line for pattern in skip_patterns):
                    continue
                    
                # 跳過太短的行（可能是導航或元素）
                if len(line) < 10:
                    continue
                    
                # 跳過主要是英文的行（同意條款等）
                if re.match(r'^[a-zA-Z\s\d\.,;&%\(\)\[\]]+$', line) and len(line) > 20:
                    continue
                    
                cleaned_lines.append(line)
            
            main_content = ' '.join(cleaned_lines)
        
        # 如果清理後的內容太短，使用標題和描述
        if len(main_content) < 50:
            return f"{title} - 詳細內容請點擊原文連結查看。"
        
        # 尋找包含關鍵字的句子
        sentences = re.split(r'[。！？]', main_content)
        key_sentences = []
        
        keywords = ['台灣', '關稅', '川普', '新聞', '發表', '宣布', '表示', '指出', '報導', '文化', '教學', '海外']
        
        for sentence in sentences:
            if len(sentence.strip()) > 15 and any(keyword in sentence for keyword in keywords):
                key_sentences.append(sentence.strip())
                if len('。'.join(key_sentences)) > max_length:
                    break
        
        if key_sentences:
            result = '。'.join(key_sentences[:2])
            if not result.endswith('。'):
                result += '。'
            return result
        else:
            # 如果沒有找到關鍵句子，取前面的句子
            result = '。'.join(sentences[:2]).strip()
            if result and not result.endswith('。'):
                result += '。'
            return result if result else main_content[:max_length] + "..."
            
    except Exception as e:
        print(f"Error in smart summary: {e}")
        return content[:max_length] + "..." if len(content) > max_length else content

@news_bp.route('/news', methods=['GET'])
def get_news():
    """獲取新聞摘要列表"""
    try:
        db = current_app.config['db']
        news_collection = db.news
        
        limit = request.args.get('limit', 10, type=int)
        
        news_items = news_collection.find().sort('created_at', -1).limit(limit)
        
        news_list = []
        for item in news_items:
            news_list.append(NewsItem.serialize_for_api(item))
        
        return jsonify(news_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@news_bp.route('/news/headlines', methods=['POST'])
def fetch_top_headlines():
    """抓取熱門頭條新聞（使用 Jina AI 抓取完整內容）"""
    try:
        db = current_app.config['db']
        news_collection = db.news
        
        crawler = NewsCrawler()
        summarizer = Summarizer()
        
        category = request.json.get('category', None)
        # News API 不支援 'tw'，改用關鍵字搜尋台灣新聞
        use_search = request.json.get('use_search', True)
        
        if use_search:
            # 使用搜尋功能來獲取台灣相關新聞
            articles = crawler.fetch_news(query='Taiwan OR 台灣', language='', page_size=5)
        else:
            # 或使用其他支援的國家
            country = request.json.get('country', 'hk')  # 香港
            articles = crawler.fetch_top_headlines(country=country, category=category)
        
        if not articles:
            return jsonify({'message': 'No headlines found'}), 404
        
        processed_count = 0
        for article in articles:
            url = article.get('url')
            if not url:
                continue
            
            existing = news_collection.find_one({'url': url})
            if existing:
                continue
            
            # 優先使用 Jina AI 抓取完整內容
            print(f"Fetching full content for: {article.get('title', 'Unknown')}")
            full_content = crawler.fetch_with_jina(url)
            
            # 如果 Jina 失敗，使用 News API 提供的內容
            if not full_content:
                full_content = article.get('content') or article.get('description', '')
                print(f"Using News API content instead of Jina for: {article.get('title', 'Unknown')}")
            
            if full_content and len(full_content) > 50:
                try:
                    # 使用 OpenAI 生成高品質摘要
                    summary = summarizer.generate_summary(
                        content=full_content,
                        title=article.get('title', ''),
                        max_length=150
                    )
                    print(f"Generated summary: {summary[:100]}...")
                except Exception as e:
                    print(f"OpenAI summary failed: {e}")
                    # 如果 OpenAI 失敗，使用更智能的簡單摘要
                    summary = create_smart_summary(full_content, article.get('title', ''), 150)
                
                news_item = NewsItem(
                    title=article.get('title'),
                    summary=summary,
                    url=url,
                    source=article.get('source'),
                    original_content=full_content
                )
                
                news_collection.insert_one(news_item.to_dict())
                processed_count += 1
                print(f"Successfully processed: {article.get('title', 'Unknown')}")
        
        return jsonify({
            'message': f'Successfully processed {processed_count} headlines',
            'total_articles': len(articles),
            'processed': processed_count
        }), 200
        
    except Exception as e:
        print(f"Error in fetch_top_headlines: {e}")
        return jsonify({'error': str(e)}), 500

@news_bp.route('/news/fetch', methods=['POST'])
def fetch_and_process_news():
    """手動觸發新聞抓取和處理（使用 Jina AI 抓取完整內容）"""
    try:
        db = current_app.config['db']
        news_collection = db.news
        
        crawler = NewsCrawler()
        summarizer = Summarizer()
        
        query = request.json.get('query', '台灣')
        
        articles = crawler.fetch_news(query=query, language='', page_size=5)
        
        if not articles:
            return jsonify({'message': 'No articles found'}), 404
        
        processed_count = 0
        for article in articles:
            url = article.get('url')
            if not url:
                continue
            
            existing = news_collection.find_one({'url': url})
            if existing:
                continue
            
            # 優先使用 Jina AI 抓取完整內容
            print(f"Fetching full content for: {article.get('title', 'Unknown')}")
            full_content = crawler.fetch_with_jina(url)
            
            # 如果 Jina 失敗，使用 News API 提供的內容
            if not full_content:
                full_content = article.get('content') or article.get('description', '')
                print(f"Using News API content instead of Jina for: {article.get('title', 'Unknown')}")
            
            if full_content and len(full_content) > 50:
                try:
                    # 使用 OpenAI 生成高品質摘要
                    summary = summarizer.generate_summary(
                        content=full_content,
                        title=article.get('title', ''),
                        max_length=150
                    )
                    print(f"Generated summary: {summary[:100]}...")
                except Exception as e:
                    print(f"OpenAI summary failed: {e}")
                    # 如果 OpenAI 失敗，使用更智能的簡單摘要
                    summary = create_smart_summary(full_content, article.get('title', ''), 150)
                
                news_item = NewsItem(
                    title=article.get('title'),
                    summary=summary,
                    url=url,
                    source=article.get('source'),
                    original_content=full_content
                )
                
                news_collection.insert_one(news_item.to_dict())
                processed_count += 1
                print(f"Successfully processed: {article.get('title', 'Unknown')}")
        
        return jsonify({
            'message': f'Successfully processed {processed_count} new articles',
            'total_articles': len(articles),
            'processed': processed_count
        }), 200
        
    except Exception as e:
        print(f"Error in fetch_and_process_news: {e}")
        return jsonify({'error': str(e)}), 500

@news_bp.route('/news/<news_id>', methods=['GET'])
def get_news_by_id(news_id):
    """根據 ID 獲取單一新聞"""
    try:
        db = current_app.config['db']
        news_collection = db.news
        
        news_item = news_collection.find_one({'_id': ObjectId(news_id)})
        
        if not news_item:
            return jsonify({'error': 'News not found'}), 404
        
        return jsonify(NewsItem.serialize_for_api(news_item)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@news_bp.route('/news/test-api', methods=['GET'])
def test_news_api():
    """測試 News API 連接"""
    import os
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        return jsonify({
            'error': 'NEWS_API_KEY not found in environment variables',
            'hint': 'Please set NEWS_API_KEY in backend/.env file'
        }), 500
    
    # 測試 API 連接
    import requests
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'us',  # 先用美國測試
        'pageSize': 1,
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'message': 'News API is working',
                'api_key_first_chars': api_key[:4] + '...',
                'test_response': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'status_code': response.status_code,
                'response': response.json()
            }), response.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@news_bp.route('/test-jina', methods=['POST'])
def test_jina():
    """測試 Jina AI 抓取功能"""
    url = request.json.get('url', 'https://www.cna.com.tw/')
    
    try:
        crawler = NewsCrawler()
        content = crawler.fetch_with_jina(url)
        
        return jsonify({
            'status': 'success',
            'url': url,
            'content_length': len(content),
            'content_preview': content[:300] + "..." if len(content) > 300 else content
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@news_bp.route('/news/test-simple', methods=['POST'])
def test_simple_fetch():
    """簡化測試：只抓取新聞不做摘要"""
    try:
        crawler = NewsCrawler()
        
        # 測試 News API
        articles = crawler.fetch_news(query='Taiwan OR 台灣', language='', page_size=5)
        
        if not articles:
            return jsonify({'error': 'No articles found'}), 404
        
        return jsonify({
            'status': 'success',
            'count': len(articles),
            'articles': articles[:2]  # 只回傳前兩篇用於測試
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@news_bp.route('/news/test-single', methods=['POST'])
def test_single_news():
    """測試單筆新聞的完整處理流程"""
    try:
        crawler = NewsCrawler()
        summarizer = Summarizer()
        
        # 獲取一筆新聞
        articles = crawler.fetch_news(query='Taiwan', language='', page_size=1)
        
        if not articles:
            return jsonify({'error': 'No articles found'}), 404
        
        article = articles[0]
        
        # 使用 Jina AI 抓取完整內容
        jina_content = crawler.fetch_with_jina(article.get('url'))
        
        result = {
            'status': 'success',
            'article': {
                'title': article.get('title'),
                'url': article.get('url'),
                'news_api_description': article.get('description', ''),
                'news_api_content': article.get('content', ''),
            },
            'jina': {
                'success': bool(jina_content),
                'content_length': len(jina_content) if jina_content else 0,
                'content_preview': jina_content[:500] + "..." if jina_content and len(jina_content) > 500 else jina_content
            }
        }
        
        # 如果 Jina 成功，生成摘要
        if jina_content and len(jina_content) > 50:
            try:
                summary = summarizer.generate_summary(
                    content=jina_content,
                    title=article.get('title', ''),
                    max_length=200
                )
                result['summary'] = {
                    'method': 'OpenAI',
                    'content': summary,
                    'length': len(summary)
                }
            except Exception as e:
                # 使用智能摘要作為備案
                summary = create_smart_summary(jina_content, article.get('title', ''), 200)
                result['summary'] = {
                    'method': 'Smart Summary (OpenAI failed)',
                    'content': summary,
                    'length': len(summary),
                    'openai_error': str(e)
                }
        else:
            result['summary'] = {
                'method': 'None',
                'content': 'Content too short or Jina failed',
                'length': 0
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500