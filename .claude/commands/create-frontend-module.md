---
description: フロントエンドに新しいモジュールを作成（5層アーキテクチャ構成）
---

フロントエンドに新しいモジュール「$ARGUMENTS」を作成してください。

## 作成するファイル構成

```
frontend/src/modules/$ARGUMENTS/
├── index.ts              # クライアントセーフなエクスポート
├── server.ts            # サーバー専用エクスポート（import 'server-only'）
│
├── ui/                  # Layer 1: UI Presentation
│   ├── ${Name}Page.tsx
│   ├── ${Name}Form.tsx
│   └── ${Name}List.tsx
│
├── model/               # Layer 4: Feature Logic
│   ├── use${Name}PageModel.ts
│   └── use${Name}FormModel.ts
│
├── api/                 # Layer 5: Domain Services
│   └── ${name}Client.ts
│
└── contract/           # 型定義・スキーマ
    ├── ${name}Contract.ts
    └── ${name}Schema.ts
```

## 実装パターン

### 1. Contract層（Zodスキーマ）
```typescript
// contract/${name}Schema.ts
import { z } from 'zod';

export const create${Name}Schema = z.object({
  name: z.string().min(1, '名前は必須です'),
  // ...
});

export type Create${Name}Input = z.infer<typeof create${Name}Schema>;
```

### 2. API層（BFF呼び出し）
```typescript
// api/${name}Client.ts
import { clientApiFetch } from '@/shared/api/client';

export async function create${Name}(data: Create${Name}Input) {
  return clientApiFetch<${Name}Response>('/api/$ARGUMENTS', {
    method: 'POST',
    body: data,
  });
}
```

### 3. Model層（React Query統合）
```typescript
// model/use${Name}PageModel.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { create${Name} } from '../api/${name}Client';

export function use${Name}PageModel() {
  const query = useQuery({
    queryKey: ['$ARGUMENTS'],
    queryFn: fetch${Name}List,
  });

  const mutation = useMutation({
    mutationFn: create${Name},
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['$ARGUMENTS'] });
    },
  });

  return {
    viewState: deriveViewState(query, mutation),
    handlers: {
      onCreate: mutation.mutate,
    },
  };
}
```

### 4. UI層（表示専用）
```tsx
// ui/${Name}Page.tsx
'use client';

import { use${Name}PageModel } from '../model/use${Name}PageModel';

export function ${Name}Page() {
  const { viewState, handlers } = use${Name}PageModel();

  if (viewState.type === 'loading') {
    return <PageSkeleton />;
  }

  if (viewState.type === 'error') {
    return <ErrorState message={viewState.error} />;
  }

  return (
    <div>
      {/* UIレンダリング */}
    </div>
  );
}
```

## BFF Route Handler

```typescript
// app/api/$ARGUMENTS/route.ts
import { proxyToBackend } from '@/shared/api/proxy';

export async function POST(request: Request) {
  return proxyToBackend(request, '/api/v1/$ARGUMENTS');
}
```

## 依存関係の方向

```
UI → Model → API → shared/api → BFF → Backend
```

## 命名規則

- コンポーネント: `${Name}Page`, `${Name}Form`
- フック: `use${Name}PageModel`, `use${Name}FormModel`
- API関数: `create${Name}`, `fetch${Name}List`
- スキーマ: `create${Name}Schema`, `${name}ResponseSchema`
- 型: `${Name}`, `Create${Name}Input`

$ARGUMENTS