# CI/CD 規則

1. 🧪 CI 步驟
   1. install dependencies
   2. lint
   3. test
   4. generate docs
   5. build
2. 🚀 CD 部署
   - 在 GitHub Actions 完成 build 後，呼叫 Zeabur CLI 部署
3. 📣 通知
   - 部署成功／失敗皆透過 Slack Webhook 回報
4. 🎯 Artifact
   - 自動上傳 coverage report 與 `docs/` 產物
