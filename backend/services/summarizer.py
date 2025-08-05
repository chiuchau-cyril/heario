import os
import re
import time
import logging
import google.generativeai as genai

# Configure performance logging for Summarizer
summarizer_logger = logging.getLogger('summarizer_performance')
summarizer_logger.setLevel(logging.INFO)
if not summarizer_logger.handlers:
    handler = logging.FileHandler('/Users/cyril/Documents/git/heario/backend/summarizer_performance.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    summarizer_logger.addHandler(handler)

class Summarizer:
    def __init__(self):
        api_key = os.getenv('GEMINI')
        if not api_key:
            print("WARNING: GEMINI API key is not set")
            self.client = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("Gemini 2.0 Flash initialized successfully")
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                self.client = None
    
    def _extract_main_content(self, content: str) -> str:
        """從 Jina AI 回應中提取主要新聞內容"""
        lines = content.split('\n')
        content_lines = []
        
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
                    if len(' '.join(content_lines)) > 1500:
                        break
                break
        
        return ' '.join(content_lines) if content_lines else content[:1000]
        
    def generate_summary(self, content: str, title: str = "", max_length: int = 200) -> str:
        """使用 Gemini 2.0 Flash 生成新聞摘要"""
        start_time = time.time()
        
        if not self.client:
            total_time = time.time() - start_time
            summarizer_logger.warning(f"GEMINI_CLIENT_UNAVAILABLE - Time: {total_time:.2f}s")
            print("Gemini client not available, using simple summary")
            return content[:max_length] + "..." if len(content) > max_length else content
            
        try:
            # 先清理內容，提取主要新聞內容
            content_cleanup_start = time.time()
            clean_content = self._extract_main_content(content)
            content_cleanup_time = time.time() - content_cleanup_start
            
            prompt = f"""
            請將以下新聞內容摘要成 {max_length} 字以內的中文摘要。
            摘要應該：
            1. 保留最重要的資訊
            2. 使用簡潔易懂的語言
            3. 適合語音播報
            4. 保持客觀中立的語氣
            5. 忽略網站導航、廣告和技術性元數據
            6. 只回傳摘要內容，不要其他解釋
            
            新聞標題：{title}
            新聞內容：{clean_content[:2000]}
            
            請提供摘要：
            """
            
            api_request_start = time.time()
            response = self.client.generate_content(prompt)
            api_request_time = time.time() - api_request_start
            
            summary = response.text.strip()
            total_time = time.time() - start_time
            
            summarizer_logger.info(f"GEMINI_SUCCESS - Title: {title[:50]}..., Content Length: {len(content)}, Clean Content Length: {len(clean_content)}, Summary Length: {len(summary)}, Content Cleanup Time: {content_cleanup_time:.2f}s, API Request Time: {api_request_time:.2f}s, Total Time: {total_time:.2f}s")
            
            return summary
            
        except Exception as e:
            total_time = time.time() - start_time
            summarizer_logger.error(f"GEMINI_ERROR - Title: {title[:50]}..., Content Length: {len(content)}, Time: {total_time:.2f}s, Error: {str(e)}")
            print(f"Error generating Gemini summary: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def batch_summarize(self, articles: list) -> list:
        """批次處理多篇文章的摘要"""
        summarized_articles = []
        
        for article in articles:
            content = article.get('content') or article.get('description', '')
            title = article.get('title', '')
            
            if content:
                summary = self.generate_summary(content, title)
                article['summary'] = summary
                summarized_articles.append(article)
        
        return summarized_articles