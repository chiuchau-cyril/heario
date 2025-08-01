# Heario 開發日誌

## 專案概述
Heario 是一個 AI 驅動的個人化新聞播報平台，包含三個階段：
- 第一階段：新聞摘要卡片（已完成主要功能）
- 第二階段：音頻 Podcast 生成
- 第三階段：虛擬主播影片

## 2025-08-01 開發進度

### 完成項目 ✅

#### 1. 專案架構建立
- Flask 後端（Python）位於 `/backend`
- React TypeScript 前端位於 `/frontend`
- MongoDB 資料庫儲存新聞資料
- 環境變數配置完成（`.env`）

#### 2. 新聞爬蟲實作
- 整合 News API（API Key: `028bb1152f82423791a6c55949af41ac`）
- 實作 Jina AI 全文抓取（API Key: `jina_beb489757c0d484e8155dc08183765d9lP8LoQ8iODZc9-zeL_fkmgwcXE-X`）
- 修正 Jina AI 內容過濾問題（移除過度嚴格的過濾規則）
- 改善內容提取算法（`extract_main_content` 函數）

#### 3. LLM 摘要功能
- ~~原始使用 OpenAI GPT-3.5（配額已用完）~~
- **已改用 Gemini 2.0 Flash**（API Key: `AIzaSyBUIeWO8U-C23oGITs7oKcsWVXxYeLnmwU`）
- 實作智能內容清理和摘要生成
- 成功生成高品質中文新聞摘要

#### 4. API 端點
- `GET /api/news` - 獲取新聞列表
- `POST /api/news/headlines` - 抓取並處理頭條新聞
- `POST /api/news/fetch` - 手動觸發新聞抓取
- `GET /api/news/<news_id>` - 獲取單一新聞
- `POST /api/news/test-single` - 測試單筆新聞處理流程
- `GET /api/news/test-api` - 測試 News API 連接
- `POST /api/test-jina` - 測試 Jina AI 功能

#### 5. 前端介面
- React TypeScript 架構
- 新聞卡片展示元件（`NewsList.tsx`）
- 響應式設計
- 與後端 API 整合（端口 3003 -> 5001）

### 關鍵問題解決記錄

#### 問題 1：Google News API 不可用
- **解決方案**：改用 News API，用戶提供了 API key

#### 問題 2：CORS 跨域請求被阻擋
- **解決方案**：在 Flask 後端加入 CORS 配置，前端設置 proxy

#### 問題 3：新聞摘要品質差，只顯示元數據
- **根本原因**：Jina AI 內容過濾過於嚴格，過濾掉了正常的內容標頭（"URL Source:", "Markdown Content:"）
- **解決方案**：
  1. 修改 `news_crawler.py` 中的 `invalid_indicators`，移除過度嚴格的過濾
  2. 實作 `extract_main_content` 函數，智能提取真正的新聞內容
  3. 改善內容清理邏輯，跳過導航元素但保留新聞正文

#### 問題 4：OpenAI 配額用完
- **解決方案**：改用 Gemini 2.0 Flash，效果更好

### 當前架構

```
backend/
├── app.py                 # Flask 主程式
├── routes/
│   └── news.py           # 新聞相關 API 路由
├── services/
│   ├── news_crawler.py   # 新聞爬蟲（News API + Jina AI）
│   └── summarizer.py     # 摘要生成（Gemini 2.0 Flash）
├── models/
│   └── news.py          # 新聞資料模型
├── test_single_news.py  # 單筆新聞測試腳本
├── clear_news.py        # 清理新聞資料腳本
└── .env                 # 環境變數（API keys）

frontend/
├── src/
│   ├── components/
│   │   └── NewsList.tsx  # 新聞列表元件
│   └── App.tsx          # 主應用程式
└── package.json         # 前端依賴
```

### 下一步開發計畫

#### 第一階段收尾
- [ ] 優化前端 UI/UX 設計
- [ ] 加入新聞分類功能
- [ ] 實作新聞更新排程（定時抓取）
- [ ] 加入使用者偏好設定

#### 第二階段：音頻功能
- [ ] 實作 TTS（文字轉語音）功能
- [ ] 建立 `/api/audio` 端點
- [ ] 前端加入音頻播放器
- [ ] 支援多語言語音

#### 第三階段：虛擬主播
- [ ] 研究虛擬角色生成技術
- [ ] 實作影片生成管道
- [ ] 整合語音和影像同步

### 重要命令備忘

```bash
# 後端啟動
cd backend
python app.py

# 前端啟動
cd frontend
npm start

# 測試單筆新聞處理
python test_single_news.py

# 清理新聞資料
python clear_news.py

# 測試 API 端點
curl -X POST http://localhost:5001/api/news/test-single
curl -X POST http://localhost:5001/api/news/headlines -H "Content-Type: application/json" -d '{"use_search": true}'
```

### 注意事項
1. MongoDB 需要先啟動（`mongod`）
2. 所有 API keys 都在 `.env` 檔案中
3. Gemini 2.0 Flash 比 OpenAI GPT-3.5 更適合中文摘要
4. Jina AI 對某些網站可能被阻擋（如部分新聞網站的反爬蟲機制）
5. 前端運行在 3003 端口，後端在 5001 端口

### 已知限制
- News API 免費版有請求次數限制
- Jina AI 某些網站無法抓取（被阻擋或需要登入）
- Gemini API 有速率限制

最後更新：2025-08-01