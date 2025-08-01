### 第一階段功能：新聞摘要卡片展示

* 使用爬蟲（[Jina.ai](http://Jina.ai) 與 Google News API）定時抓取
* 使用 LLM（GPT）生成 150~300 字摘要
* 儲存至 MongoDB
* 前端以 React / Vue 呈現卡片 UI

### 第二階段功能：語音 Podcast 串流

* TTS 使用 OpenAI Whisper 或自行轉換為語音檔
* 串流方式：Cloudflare Stream + WebRTC SDK
* 前端整合 Podcast 播放元件，可播放、快轉、暫停

### 第三階段功能：虛擬主播影片

* 虛擬角色建立方式（尚未選定工具，考慮 Adobe Animate）
* TTS 語音 + LipSync 嘴型同步（工具尚待研究）
* 影片生成後使用 HLS 串流播放

### 用戶與內容管理

* 用戶註冊與站台建立（自選主題 / 關鍵字）
* 自訂頻道與 RSS 整合
* 生成個人站台分享連結
* 支援社群分享（LINE、Facebook、X）

### 授權與資料使用規範

* 所有播報內容由 AI 生成摘要，不重製原始新聞全文
* 顯示新聞來源與原始連結
* RSS 與新聞摘要使用遵循 Fair Use 原則

### 技術選型與基礎建設

* 後端：Flask 或 Django，提供 API
* 前端：React
* 資料庫：MongoDB
* TTS：OpenAI Whisper（後續可替換）
* 串流：WebRTC + Cloudflare Stream
* 託管：可部署於 Cloud Run、Vercel、Render、或本地測試伺服器

### 擴充與商業化項目

* 廣告 SDK 整合（Google AdSense）
* 用戶付費訂閱功能（如自定聲音 / 無廣告體驗）
* 虛擬主播角色商店（進階）

### 後續規劃建議

* 調查使用者收聽與觀看習慣數據
* 導入即時互動（如語音留言、觀眾投票）
* 與媒體合作建立授權內容資料夾
