# Backend Context Pack (固定コンテキスト)

## 0) 技術と構造

- FastAPI + Python
- Clean Architecture: API → Application → Domain → Infrastructure
- tests: unit / integration / integration_real（既存の運用に従う）

## 1) 依存方向（絶対）

- Domain はフレームワーク/DB/外部サービスに依存しない
- Application は Port（IF）に依存し、Infra はそれを実装
- API は DI で wiring するだけ（ビジネスロジックを肥大化させない）

## 2) 例外とエラー設計

- Domain/Application のエラーを HTTP にマッピングする
- 例外の握りつぶし禁止（原因の所在が不明になる）

## 3) テスト方針

- Domain/Application：unit を厚く
- API/DI/DB：integration を追加
- 変更時は「どの層に影響したか」を明記し、対応テストを示す
