# MSW モック実装ガイド

このプロジェクトでは、[MSW (Mock Service Worker)](https://mswjs.io/)を使用して API のモックを実装しています。

## 概要

MSW はブラウザレベルで HTTP リクエストをインターセプトし、モックレスポンスを返すことができます。これにより、バックエンド API が未実装でもフロントエンドの開発を進めることができます。

## セットアップ

### 1. 環境変数の設定

`.env.local`ファイル（または`.env.development`）に以下を追加：

```env
NEXT_PUBLIC_USE_MOCK=true
```

### 2. 開発サーバーの起動

```bash
pnpm dev
```

モックが有効化されている場合、コンソールに `✅ MSWモックが有効化されました` と表示されます。

## 使用方法

### モックの有効化/無効化

環境変数 `NEXT_PUBLIC_USE_MOCK` で制御します：

- `true`: モックを有効化
- `false` または未設定: モックを無効化（実際の API に接続）

### モックデータのカスタマイズ

`lib/mocks/handlers.ts` を編集して、モックデータやレスポンスを変更できます。

例：

```typescript
const mockUser: UserSummaryApi = {
  id: 'mock-user-id',
  email: 'custom@example.com', // カスタマイズ
  name: 'カスタムユーザー',
  // ...
};
```

### 新しいエンドポイントの追加

`lib/mocks/handlers.ts` の `handlers` 配列に新しいハンドラーを追加：

```typescript
http.get(`${API_BASE_URL}/your-endpoint`, () => {
  return HttpResponse.json({
    // モックレスポンス
  });
}),
```

## ファイル構成

```
lib/mocks/
├── handlers.ts    # モックハンドラーの定義
├── browser.ts     # ブラウザ環境用のセットアップ
├── server.ts      # サーバー環境（テスト用）のセットアップ
└── index.ts       # モック有効化の判定ロジック

components/mocks/
└── MockProvider.tsx  # MSWを初期化するReactコンポーネント

public/
└── mockServiceWorker.js  # MSWのService Worker（自動生成）
```

## テストでの使用

テスト環境では `lib/mocks/server.ts` を使用します：

```typescript
import { server } from '@/lib/mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 注意事項

1. **本番環境では無効化**: モックは開発環境でのみ使用してください
2. **Service Worker のキャッシュ**: ブラウザの開発者ツールで Service Worker をクリアする必要がある場合があります
3. **型安全性**: モックレスポンスは実際の API 型と一致させることを推奨します

## トラブルシューティング

### モックが動作しない

1. 環境変数 `NEXT_PUBLIC_USE_MOCK=true` が設定されているか確認
2. ブラウザの開発者ツールで Service Worker が登録されているか確認
3. コンソールにエラーがないか確認
4. 開発サーバーを再起動

### Service Worker の更新

Service Worker のファイルを更新した場合、ブラウザでハードリロード（Ctrl+Shift+R / Cmd+Shift+R）が必要な場合があります。
