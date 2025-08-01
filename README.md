# Heario - AI 驅動的個人新聞播報平台

Heario 是一個 AI 驅動的個人新聞站台平台，自動抓取、摘要並播報新聞內容。

## 功能特色

- 🤖 使用 AI 自動生成新聞摘要
- 📰 整合 News API 獲取新聞（支援頭條新聞和關鍵字搜尋）
- 🔍 使用 Jina.ai 爬蟲獲取完整內容
- 🎙️ 語音播報功能（開發中）
- 👤 虛擬主播影片（規劃中）

## 技術架構

- **前端**: React + TypeScript
- **後端**: Flask + Python
- **資料庫**: MongoDB
- **AI 服務**: OpenAI GPT-3.5

## 快速開始

### 環境需求

- Node.js 18+
- Python 3.8+
- MongoDB

### 後端設定

1. 進入後端目錄：
```bash
cd backend
```

2. 建立虛擬環境並安裝套件：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 設定環境變數：
```bash
cp .env.example .env
# 編輯 .env 檔案，填入你的 API keys
```

4. 啟動 Flask 伺服器：
```bash
python app.py
```

### 前端設定

1. 進入前端目錄：
```bash
cd frontend
```

2. 安裝套件：
```bash
npm install
```

3. 啟動開發伺服器：
```bash
npm start
```

### MongoDB 設定

確保 MongoDB 正在執行：
```bash
# macOS (使用 Homebrew)
brew services start mongodb-community

# 或直接執行
mongod
```

## API 端點

- `GET /api/news` - 獲取新聞摘要列表
- `POST /api/news/fetch` - 手動觸發新聞抓取
- `GET /api/news/{id}` - 獲取單一新聞詳情
- `GET /api/audio` - 獲取 TTS 音訊（開發中）
- `GET /api/rss` - 獲取 RSS feed（開發中）

## 使用說明

1. 開啟瀏覽器訪問 http://localhost:3000
2. 點擊「台灣頭條」按鈕來獲取台灣最新頭條新聞
3. 或點擊「搜尋新聞」來搜尋特定關鍵字的新聞
4. 新聞會自動生成 AI 摘要並顯示在卡片中
5. 點擊「閱讀原文」可以查看完整新聞

## 需要的 API Keys

在 `backend/.env` 檔案中設定以下 API keys：
- `NEWS_API_KEY`: 從 https://newsapi.org/ 申請
- `OPENAI_API_KEY`: 從 https://platform.openai.com/ 申請
- `JINA_API_KEY`: 從 https://jina.ai/ 申請（選用）

## 開發進度

- [x] 第一階段：新聞摘要卡片
- [ ] 第二階段：語音播報功能
- [ ] 第三階段：虛擬主播影片

## 授權

本專案採用 MIT 授權