# Google Cloud TTS 設定指南

## 1. 環境變數設定

在後端目錄中設定環境變數：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/../heario-4099f-ad430d303592.json"
```

## 2. 安裝依賴

```bash
pip install -r requirements.txt
```

## 3. 測試 TTS 服務

```bash
python test_tts.py
```

## 4. 可用的中文語音

- `cmn-TW-Standard-A`: 台灣中文標準語音 (女聲)
- `cmn-TW-Standard-B`: 台灣中文標準語音 (男聲)
- `cmn-TW-Standard-C`: 台灣中文標準語音 (女聲)
- `cmn-TW-Wavenet-A`: 台灣中文高品質語音 (女聲)
- `cmn-TW-Wavenet-B`: 台灣中文高品質語音 (男聲)
- `cmn-TW-Wavenet-C`: 台灣中文高品質語音 (女聲)

## 5. 語言代碼

- `cmn-TW`: 台灣中文 (繁體)
- `cmn-CN`: 中國中文 (簡體)
- `yue-HK`: 香港粵語
- `en-US`: 美式英語

## 6. 注意事項

- 確保 Google Cloud 專案已啟用 Text-to-Speech API
- 服務帳戶金鑰檔案必須有適當的權限
- 語音合成會產生 MP3 格式的音頻檔案 