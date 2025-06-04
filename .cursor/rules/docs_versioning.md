# 文件版本化規範

1. 📁 所有文件放在 `docs/` 目錄
2. 📝 文件變動必須同步 commit
   - 使用 `docs(scope): 描述` 作為 commit type
3. 🚧 API 定義
   - 請使用 OpenAPI v3 YAML/JSON
   - 放置於 `docs/api/openapi.yaml`
   - 每次 PR 合併時，CI 自動生成 `docs/api/openapi.json`
4. 🔄 架構圖
   - `docs/architecture.md` 採 Markdown＋PlantUML
   - CI 可透過 PlantUML CLI 定期渲染 PNG
