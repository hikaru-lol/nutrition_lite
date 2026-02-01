# 型の置き場所 & 型変換ルール（Frontend Strict）

## 0) 目的

- **型の真実（Source of Truth）を 1 箇所に寄せる**
- **変換・検証を境界で行い、内側を安定化する**
- **UI に API 都合を漏らさない**

---

## 1) 型のカテゴリ定義

### A. Contract 型（DTO / Schema）

- **意味**：BFF が受け取る/返す JSON の仕様（Request/Response）
- **実体**：Zod schema + TS type（infer）
- **置き場所**：`modules/<feature>/contract/*`

### B. Model 型（ViewModel / Form / PageState）

- **意味**：UI が直接扱う“画面用の形”（フォーム値、表示用、導出状態）
- **置き場所**：`modules/<feature>/model/*`

### C. Shared 型（共通部品だけ）

- **意味**：複数 feature で共通な小さな構造（Pagination, DateISO, ApiError など）
- **置き場所**：`shared/*`（例：`shared/api/contracts`）

---

## 2) 依存方向（型参照もこれに従う）

**UI → Model → API → shared/api → BFF → Backend**

- `contract` は **参照されるだけ**（どこも import しない）
- UI は **Model しか見ない**（contract/api/shared/api を見ない）

---

## 3) 型の置き場所ルール（結論）

### ✅ Contract（DTO/Schema）

- `modules/<feature>/contract/*.ts`
- contract は **純粋**に保つ（Zod/TS のみ）
- **禁止**：React Query / fetch / UI / shared/api import

### ✅ API（通信）

- `modules/<feature>/api/*.ts`
- ここは **BFF への呼び出し**のみ
- **使用できる通信手段は `clientApiFetch` のみ**
- ここで **レスポンス parse（Zod）**して「保証済み DTO」を返す

### ✅ Model（画面用変換）

- `modules/<feature>/model/*.ts`
- API から受け取った DTO を **UI 用の shape に変換**
- フォーム入力を **parse**して **API 送信値に確定**（input→output）

### ✅ UI（表示）

- `modules/<feature>/ui/*.tsx`
- import できるのは **Model のみ**
- エラー/ローディングは **Model が出す状態**を見て表示するだけ

---

## 4) “型変換”の置き場所ルール（超重要）

### 4.1 API 層でやる変換（境界の正規化）

**BFF レスポンス（unknown）→ Contract 型**への変換・検証

- `modules/<feature>/api/*` でやる
- `Schema.parse(raw)` をここで実行
- 失敗したら例外（契約違反）

例：

```ts
// modules/profile/api/profileClient.ts
const raw = await clientApiFetch<unknown>('/profile');
return ProfileSchema.parse(raw);
```

---

### 4.2 Model 層でやる変換（UI 向け整形・導出）

**Contract 型 → UI 用 ViewModel/Form/PageState** の変換

例：

- `defaults`（フォーム初期値）
- `activeTarget` の導出
- `age`, `label`, `chartData` など表示用に加工

---

### 4.3 フォーム値の input/output ルール（Zod v4 重要）

`z.coerce` / `transform` を使うスキーマは **input 型と output 型が異なる**。

#### ✅ ルール

- フォームで扱う型：`z.input<typeof Schema>`
- API へ送る直前：`Schema.parse(values)` で output に確定して送る

例：

```ts
export type FormValues = z.input<typeof ProfileFormSchema>;
type Parsed = z.output<typeof ProfileFormSchema>;

async function save(v: FormValues) {
  const parsed: Parsed = ProfileFormSchema.parse(v);
  return api.upsertProfile(parsed);
}
```

---

## 5) エラーハンドリングの配置（型運用とセット）

### shared/api（共通）

- HTTP エラーを **共通例外（ApiError）に正規化**して throw
- feature 固有メッセージは入れない

### modules/\*/api

- Zod parse 失敗（契約違反）を検知して throw（またはそのまま throw）
- ここは “境界エラー” の責任

### modules/\*/model

- `error` を **画面状態**に変換（表示文言、リトライ可否、遷移方針）
- UI は `isError` や `errorMessage` を表示するだけ

---

## 6) 禁止パターン（アンチパターン）

- UI が `modules/*/api` や `shared/api` を import する ❌
- Model が `shared/api` を直接叩く（API 層を飛ばす）❌
- contract が `@tanstack/*` や `react` を import する ❌
- shared/api に feature の parse/変換ロジックを入れる ❌
- backend を直接叩く（BFF を経由しない）❌

---

## 7) 機械的チェックリスト（PR で見る場所）

- `modules/*/ui/**` の import に `../api` や `@/shared/api` が無い ✅
- `modules/*/model/**` が `../api` を経由している ✅
- `modules/*/api/**` が `clientApiFetch` 以外で通信していない ✅
- `modules/*/contract/**` が Zod/TS 以外を import していない ✅
- `app/api/**` が `server-only` の proxy を使っている ✅
