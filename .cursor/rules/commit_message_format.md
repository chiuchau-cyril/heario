# Commit Message Format

- 第一行（Header）不得超過 72 字元 ** **
- 第二行留空 ** **
- 第三行開始（Body）可寫更詳細的描述 ** **
- 為何做這些改動 ** **
- 影響哪些模組 ** **
- 任何注意事項 ** **
- 範例：
  - feat(auth): 支援第二階段 OTP 驗證
  - 新增 /otp/send 及 /otp/verify API
  - 更新前端登入流程，加入 OTP 驗證步驟
  - 相關單元測試覆蓋率 100%
