# Git Policy

1. 🏷 Branch 命名
   - feature/<short-desc>  
   - fix/<short-desc>  
   - chore/<short-desc>  
2. 🔀 Pull Request
   - 每個 branch 完成後開 PR，目標 branch 為 main 或 develop
   - PR 標題：<type>(<scope>): <簡短描述>
3. 📦 Commit Message
   - 使用 Conventional Commits：
     - feat(scope): 新功能簡述
     - fix(scope): 修正簡述
     - docs(scope): 文件相關
     - chore(scope): 重構、CI、設定
   - Footer 可選填：
     - [可選] 詳細原因、影響範圍、關聯 Issue #ID
4. 📝 文件
   - 所有新增功能、設定、重構等，需更新 README.md 或相關文件
   - 文件更新後，需更新版本號
5. 🔄 版本控制
   - 每次發布新版本時，需更新 package.json 中的版本號
   - 版本號格式：MAJOR.MINOR.PATCH
   - 版本號更新規則：
     - MAJOR：重大變更，可能破壞現有功能
     - MINOR：新功能、功能增強
     - PATCH：錯誤修正、小規模調整
