# Google Cloud Text-to-Speech 設定指南

## 📋 設定步驟

### 1. 建立 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊「建立專案」或選擇現有專案
3. 記下您的專案 ID

### 2. 啟用 Text-to-Speech API
1. 在 Google Cloud Console 中，前往「API 和服務」>「資料庫」
2. 搜尋「Cloud Text-to-Speech API」
3. 點擊並啟用該 API

### 3. 建立服務帳戶
1. 前往「IAM 和管理」>「服務帳戶」
2. 點擊「建立服務帳戶」
3. 輸入服務帳戶名稱（例如：heario-tts）
4. 在「角色」中選擇「Cloud Text-to-Speech 用戶端」
5. 點擊「完成」

### 4. 建立並下載金鑰
1. 在服務帳戶列表中，點擊您剛建立的服務帳戶
2. 切換到「金鑰」分頁
3. 點擊「新增金鑰」>「建立新金鑰」
4. 選擇「JSON」格式
5. 下載金鑰檔案（例如：heario-tts-key.json）

### 5. 設定環境變數
將下載的 JSON 金鑰檔案放在安全的位置，然後設定環境變數：

```bash
# 方法 1: 設定環境變數
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/heario-tts-key.json"

# 方法 2: 加入到 .env 檔案
echo 'GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/heario-tts-key.json' >> .env
```

### 6. 測試設定
```bash
python test_tts.py
```

## 🎯 API 限制與計費

### 免費額度（每月）
- **標準語音**: 4,000,000 字元
- **WaveNet 語音**: 1,000,000 字元
- **Neural2 語音**: 1,000,000 字元

### 計費標準
- **標準語音**: 每百萬字元 $4.00 USD
- **WaveNet 語音**: 每百萬字元 $16.00 USD
- **Neural2 語音**: 每百萬字元 $16.00 USD

### 推薦設定
對於 Heario 專案，建議：
1. 開發時使用**標準語音**（便宜且品質良好）
2. 生產環境可考慮升級到 **Neural2 語音**（品質更佳）

## 🔧 故障排除

### 常見錯誤

1. **認證錯誤**
   ```
   google.auth.exceptions.DefaultCredentialsError
   ```
   **解決方案**: 確認 GOOGLE_APPLICATION_CREDENTIALS 環境變數已正確設定

2. **專案權限錯誤**
   ```
   USER_PROJECT_DENIED
   ```
   **解決方案**: 確認已啟用 Text-to-Speech API 且服務帳戶有正確權限

3. **配額超限**
   ```
   QUOTA_EXCEEDED
   ```
   **解決方案**: 檢查 Google Cloud Console 中的配額使用情況

### 測試指令
```bash
# 測試基本 TTS 功能
python test_tts.py

# 測試 API 端點
curl -X GET http://localhost:5001/api/audio/test

# 測試文字合成
curl -X POST http://localhost:5001/api/audio/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "這是測試文字"}'
```

## 📱 Heario 整合

設定完成後，Heario 的以下功能將可用：
- ✅ 播放清單音頻生成
- ✅ 單一新聞音頻生成
- ✅ 中英文混合語音合成
- ✅ 自動語言偵測
- ✅ 音頻檔案下載

開始使用 TTS 功能吧！🎉