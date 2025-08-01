# CLAUDE.md - Heario 專案開發指南

## 專案概述
Heario 是一個 AI 驅動的個人化新聞播報平台，使用 Flask 後端和 React 前端。

## 重要資訊

### API Keys（已配置在 .env）
- **News API**: `028bb1152f82423791a6c55949af41ac`
- **Jina AI**: `jina_beb489757c0d484e8155dc08183765d9lP8LoQ8iODZc9-zeL_fkmgwcXE-X`
- **Gemini**: `AIzaSyBUIeWO8U-C23oGITs7oKcsWVXxYeLnmwU`

### 技術選擇
- **後端**: Flask (Python)
- **前端**: React + TypeScript
- **資料庫**: MongoDB
- **新聞來源**: News API
- **全文抓取**: Jina AI
- **摘要生成**: Gemini 2.0 Flash（不使用 OpenAI）

### 重要提醒
1. **使用 Gemini 而非 OpenAI**：專案已改用 Gemini 2.0 Flash 進行摘要生成
2. **Jina AI 內容過濾已修正**：不要過濾 "URL Source:" 和 "Markdown Content:"
3. **使用智能內容提取**：`extract_main_content` 函數會自動提取真正的新聞內容

### 常見問題解決
- **CORS 錯誤**: 確保 Flask 有正確的 CORS 配置
- **摘要品質差**: 檢查 Jina AI 內容是否被過度過濾
- **API 配額問題**: 使用 Gemini 而非 OpenAI

### 開發流程
1. 啟動 MongoDB: `mongod`
2. 啟動後端: `cd backend && python app.py`
3. 啟動前端: `cd frontend && npm start`
4. 測試功能: 使用 `test_single_news.py` 測試單筆新聞處理

### 下次開發重點
- 實作 TTS 音頻功能（第二階段）
- 優化前端 UI 設計
- 加入定時新聞更新功能