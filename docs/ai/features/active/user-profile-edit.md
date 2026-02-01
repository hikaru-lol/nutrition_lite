# ユーザープロフィール編集機能

## ステータス: ✅ 完了

## 概要

ユーザーが自分のプロフィール情報（ユーザー名、メール、自己紹介）を編集できる機能

## 技術仕様

### バックエンド

- **エンドポイント**:
  - `GET /api/v1/users/me` - プロフィール取得
  - `PUT /api/v1/users/me` - プロフィール更新
- **認証**: Cookie-based（既存）
- **バリデーション**: Pydantic (min/max 長、email 形式)

### フロントエンド

- **ページ**: `app/(auth)/profile/page.tsx`
- **コンポーネント**:
  - `features/profile-edit/ui/ProfileEditForm.tsx`
  - `entities/user/ui/UserAvatar.tsx`
- **バリデーション**: Zod + react-hook-form
- **状態管理**: Zustand (profile-edit feature)

## 実装タスク

### Phase 1: バックエンド API ✅

- [x] Pydantic スキーマ定義 (`UserUpdate`, `UserResponse`)
- [x] リポジトリメソッド (`update_user`)
- [x] サービス層ロジック (重複チェック)
- [x] エンドポイント実装
- [x] OpenAPI ドキュメント更新
- [x] テスト作成 (`tests/api/test_users.py`)

### Phase 2: フロントエンド ✅

- [x] エンティティ層 (`entities/user`)
  - [x] 型定義 (`UserSchema`)
  - [x] API クライアント (`userApi.updateMe`)
  - [x] UI コンポーネント (`UserAvatar`)
- [x] フィーチャー層 (`features/profile-edit`)
  - [x] 状態管理 (`useProfileEdit`)
  - [x] フォームコンポーネント (`ProfileEditForm`)
- [x] ページ統合 (`app/(auth)/profile/page.tsx`)
- [x] テスト作成

### Phase 3: 統合テスト ✅

- [x] E2E テスト (Playwright)
- [x] バックエンドテスト全通過
- [x] フロントエンドテスト全通過

## 参考ドキュメント

- `docs/ai/backend-guide.md` - クリーンアーキテクチャパターン
- `docs/ai/frontend-guide.md` - FSD 実装パターン
- `docs/ai/auth-implementation.md` - 認証フロー

## 実装の学び・メモ

### 実装時の決定事項

- ユーザー名の重複チェックはサービス層で実施
- アバター画像は Phase 1 では対象外（将来拡張）
- バリデーションエラーは統一フォーマットでフロントに返却

### トラブルシューティング

- **問題**: Cookie 認証が localhost で動作しない
- **解決**: `withCredentials: true`を axios 設定に追加

### パフォーマンス考慮

- プロフィール更新は楽観的 UI は不要（頻度低い）
- 更新後はキャッシュを即座に invalidate

## Git 履歴

- Commit: `feat: implement user profile edit feature`
- PR: #42
- Merged: 2026-01-28
