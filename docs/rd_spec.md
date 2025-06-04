# Heario 需求規格書（RD Spec）

---

## 一、專案簡介
Heario 是一個 AI 驅動的個人新聞站台平台，結合新聞摘要、語音播報與虛擬主播影片，主打自動化、個人化與易用性，服務對象為通勤族、Podcast 使用者與一般大眾。

---

## 二、目標與市場定位
- 目標用戶：一般大眾、通勤族、Podcast 愛好者、資訊工作者
- 商業模式：廣告與訂閱制，未來發展 SaaS 服務
- 市場趨勢：TTS、Podcast、虛擬主播市場皆高速成長，台灣用戶有晨間聽新聞需求

---

## 三、功能需求
### 1. 新聞摘要卡片
- 自動爬取新聞（Jina.ai、Google News API）
- LLM（GPT）生成 150~300 字摘要
- 前端以卡片方式展示，顯示標題、摘要、原始連結，按時間排序
- 點擊卡片可於新分頁開啟原始新聞

### 2. 語音新聞（Podcast 串流）
- TTS（Whisper API/edge-tts）自動生成語音
- 前端卡片下方提供播放/暫停按鈕，支援 mp3/ogg
- 用戶可選擇語音風格（登入後）
- 串流方式：Cloudflare Stream + WebRTC
- 提供 RSS feed，支援 Spotify/Apple Podcast 訂閱

### 3. 個人新聞站台與分享
- 註冊用戶可自訂主題/關鍵字，建立個人頻道
- 每日自動產出摘要卡
- 生成可分享的個人站台連結，支援公開瀏覽與社群分享

### 4. 虛擬主播影片
- 高階用戶可選擇虛擬主播朗讀新聞，支援角色選擇與 LipSync
- 影片可嵌入網站/部落格，提供 iframe 代碼
- 影片串流：HLS/WebRTC

### 5. 商業機制
- 後台整合廣告平台（Google AdSense/Firstory）
- 支援用戶升級訂閱，享無廣告與客製化功能（專屬語音/影片風格）
- 點擊與曝光數據追蹤

### 6. 用戶與內容管理
- 用戶註冊、登入（OAuth）
- 偏好設定（主題、語音風格）
- 內容授權與 Fair Use 規範

---

## 四、API 介面規格（摘要）
- `GET /api/news`：取得新聞摘要卡片列表
- `GET /api/audio?id=xxx`：取得指定新聞的語音檔
- `GET /api/video?id=xxx`：取得虛擬主播影片（高階用戶）
- `GET /api/rss`：取得 Podcast RSS feed
- `POST /api/user/login`：OAuth 登入
- `POST /api/user/preferences`：設定用戶偏好
- `POST /api/feedback`：回報意見

---

## 五、系統架構與技術選型
- 前端：React（或 Vue.js）
- 後端：Flask 或 Django，RESTful API
- 資料庫：MongoDB / MySQL
- TTS：Whisper API / edge-tts
- 影片生成：LipSync + Animate/Unity
- 串流：Cloudflare Stream、WebRTC、HLS
- 託管：Cloud Run、Vercel、Render

---

## 六、品質目標
- 易用性：介面直覺、低學習門檻
- 音訊延遲 < 1 秒，影片延遲 < 5 秒
- 可擴展性：模組化設計，支援 plug-and-play
- 可維運性：簡易日誌、雲端監控

---

## 七、風險與挑戰
- 中文 TTS/LLM 資料偏簡體，需優化台灣語境
- 虛擬主播互動性與自然度需精緻設計
- 版權與新聞摘要使用界線需嚴格控管
- Cloudflare Stream 成本與流量規劃

---

## 八、後續擴充建議
- 廣告 SDK、訂閱制、虛擬角色商店
- 即時互動（語音留言、投票）
- 與媒體合作授權內容

---

## 九、名詞解釋
- LLM：大型語言模型
- TTS：文字轉語音
- HLS：HTTP Live Streaming
- WebRTC：網頁即時通訊
- MVP：最小可行性產品
