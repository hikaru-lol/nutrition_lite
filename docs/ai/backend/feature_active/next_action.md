今後のタスク整理

  🎯 次に進むべき主要タスク

  1. フロントエンド側のカレンダー機能実装

  - 場所: frontend/src/modules/calendar/
  - 必要なもの:
    - カレンダーコンポーネント（月次ビュー）
    - API契約 (contract)
    - モデル (hooks, state management)
    - UI コンポーネント (CalendarPage, CalendarGrid, DayCard)
  - 参考: 既存のmodules/today/, modules/target/パターン

  2. 統合テストの実装

  - 場所: backend/tests/integration/api/test_calendar.py
  - 内容:
    - API エンドポイントの結合テスト
    - 認証フローとの統合
    - エラーケースの検証

  3. マイグレーション検討

  - 確認点:
  カレンダー機能で使用するDBテーブルが既存スキーマで対応可能か
  - テーブル: food_entries, daily_nutrition_summaries,
  daily_nutrition_reports, targets
  - 結果: 新規マイグレーションは不要（既存テーブル活用）

  4. デプロイメント準備

  - OpenAPI仕様更新:
  docs/openapi/openapi.yamlにカレンダーエンドポイント追加
  - 環境変数確認: 特に新規追加は不要
  - CI/CD: 既存のテストパイプラインで対応済み

  📦 現在の状況

  ✅ 完了済み
  - バックエンドAPI実装（Clean Architecture準拠）
  - ユニットテスト（17件全成功）
  - 型安全性とコード補完対応

  📝 Git状態
  - 修正ファイル: 20件（既存ファイルの更新）
  - 新規ファイル: 10件（カレンダー機能関連）
  - まだコミットしていない

  🚀 推奨する進行順序

  1. フロントエンド実装 - バックエンドAPIを活用
  2. 統合テスト - エンドツーエンドの動作確認
  3. OpenAPI仕様更新 - ドキュメント整備
  4. 最終テスト & コミット - 機能完成

  どのタスクから始めますか？

● How is Claude doing this session? (optional)
  1: Bad    2: Fine   3: Good   0: Dismiss