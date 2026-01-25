# Global Context (Monorepo)

## Repo layout

- backend/: FastAPI + Python (Clean Architecture)
- frontend/: Next.js 16 App Router + TypeScript (Feature Sliced)
- docs/openapi/: OpenAPI spec (if used)
- docs/ai/: AI 運用の正本（ここを参照して作業）

## Operating principles

- Doc-in-Code: 仕様はコード（型/契約/ViewState/テスト）に置く
- Minimal diff, plan-first, verify-always
- FE/BE を跨ぐ変更は必ずチェックリスト化（OpenAPI/Contracts/BFF）

## Commands

- Backend dev: `cd backend && uvicorn app.main:app --reload`
- Frontend dev: `cd frontend && pnpm dev`
- Backend tests: `cd backend && pytest`
