# モーダル5層アーキテクチャリファクタリング設計ガイド

## 概要

このドキュメントは、TodayPageContentのモーダル管理を5層レイヤードアーキテクチャにリファクタリングする際の設計思想、実装パターン、及び実際の実装例を記録したものです。

## 設計思想

### 1. 責務の明確な分離
- モーダル状態管理はUI機能であり、Layer 2 (UI Orchestration) に属する
- ページレベルのロジック（Layer 3）からモーダル固有の状態管理を分離
- 再利用可能性と保守性を向上

### 2. Container/Presentational パターンの適用
- モーダル状態管理ロジック（Container）とUI表現（Presentational）を分離
- プロップスによる制御でテスタビリティを向上

### 3. 段階的移行戦略
- 既存システムを壊さずに新アーキテクチャを導入
- 一つのモーダルから始めて段階的に適用

## 5層アーキテクチャにおけるモーダルの位置づけ

```
┌─────────────────────────────────────────┐
│ Layer 1: UI Presentation                │ ← Modal Component (AddMealModal)
├─────────────────────────────────────────┤
│ Layer 2: UI Orchestration               │ ← Modal State Hook (useAddMealModalState)
├─────────────────────────────────────────┤
│ Layer 3: Page Aggregation               │ ← Page Component (TodayPageContent)
├─────────────────────────────────────────┤
│ Layer 4: Feature Logic                  │ ← Business Logic (useMealManagement)
├─────────────────────────────────────────┤
│ Layer 5: Domain Services                │ ← API Calls (mealService)
└─────────────────────────────────────────┘
```

### 責務分担

- **Layer 1**: モーダルUIコンポーネントの表現
- **Layer 2**: モーダル状態管理・開閉制御・パラメータ管理
- **Layer 3**: ページ全体の協調・モーダル統合・ビジネスロジック呼び出し
- **Layer 4**: データフェッチング・CRUD操作・状態管理
- **Layer 5**: API通信・データ変換

## 実装パターン

### Step 1: Layer 2 Hook作成

```typescript
// modules/{module}/ui/hooks/use{Modal}ModalState.ts

/**
 * use{Modal}ModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - {Modal}の状態管理
 * - モーダルの開閉制御
 * - フォームパラメータの管理
 */

'use client';

import { useState, useCallback } from 'react';

// ========================================
// Types
// ========================================

export interface {Modal}ModalState {
  isOpen: boolean;
  // モーダル固有の状態プロパティ
}

export interface {Modal}ModalActions {
  open: (...params) => void;
  close: () => void;
}

export interface {Modal}ModalModel extends {Modal}ModalState, {Modal}ModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function use{Modal}ModalState(): {Modal}ModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  // その他のモーダル固有状態

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((...params) => {
    // パラメータ設定ロジック
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    // その他の状態

    // Actions
    open,
    close,
  };
}
```

### Step 2: Page Component統合

```typescript
// Before: インライン状態管理
const [isModalOpen, setIsModalOpen] = useState(false);
const [modalParam, setModalParam] = useState();

const handleOpen = (param) => {
  setModalParam(param);
  setIsModalOpen(true);
};

// After: 専用Hook使用
// ========================================
// Layer 2: UI Orchestration Hooks
// ========================================
const modalState = use{Modal}ModalState();

const handleOpen = (param) => modalState.open(param);
```

### Step 3: イベントハンドラー簡潔化

```typescript
// Before: 複数行のセットアップ
const handleOpen = (param1, param2) => {
  setParam1(param1);
  setParam2(param2);
  setIsModalOpen(true);
};

const handleSubmit = async (values) => {
  await businessLogic(values);
  setIsModalOpen(false);
};

// After: 1行の呼び出し
const handleOpen = (param1, param2) => modalState.open(param1, param2);

const handleSubmit = async (values) => {
  await businessLogic(values);
  modalState.close();
};
```

### Step 4: Modal Component Props更新

```typescript
// Before: 複数の個別props
<Modal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  param1={param1}
  param2={param2}
  // ... other props
/>

// After: Hook統合props
<Modal
  isOpen={modalState.isOpen}
  onClose={modalState.close}
  param1={modalState.param1}
  param2={modalState.param2}
  // ... other props
/>
```

## 実装例（Add Meal Modal）

### 1. Hook Implementation

```typescript
// /workspace/frontend/src/modules/today/ui/hooks/useAddMealModalState.ts

/**
 * useAddMealModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - 食事追加モーダルの状態管理
 * - モーダルの開閉制御
 * - フォームパラメータの管理
 */

'use client';

import { useState, useCallback } from 'react';

// ========================================
// Types
// ========================================

export interface AddMealModalState {
  isOpen: boolean;
  selectedMealType: 'main' | 'snack';
  selectedMealIndex: number;
}

export interface AddMealModalActions {
  open: (mealType: 'main' | 'snack', mealIndex?: number) => void;
  close: () => void;
}

export interface AddMealModalModel extends AddMealModalState, AddMealModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function useAddMealModalState(): AddMealModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');
  const [selectedMealIndex, setSelectedMealIndex] = useState(1);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    setSelectedMealType(mealType);
    if (mealType === 'main' && mealIndex) {
      setSelectedMealIndex(mealIndex);
    }
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    selectedMealType,
    selectedMealIndex,

    // Actions
    open,
    close,
  };
}
```

### 2. Page Integration

```typescript
// TodayPageContent.tsx

import { useAddMealModalState } from './hooks/useAddMealModalState';

export function TodayPageContent({ date }: TodayPageContentProps) {
  // ... other hooks

  // ========================================
  // Layer 2: UI Orchestration Hooks
  // ========================================
  const addMealModal = useAddMealModalState();

  // ... other code

  const handleAddClick = (mealType: 'main' | 'snack', mealIndex?: number) => {
    addMealModal.open(mealType, mealIndex);
  };

  const handleAddModalSubmit = async (values: AddMealFormValues) => {
    await m.meals.addMeal(values);
    addMealModal.close();
  };

  return (
    <div className="w-full space-y-6">
      {/* ... other content */}

      {/* 食事追加モーダル - Layer 2: UI Orchestration */}
      <AddMealModal
        isOpen={addMealModal.isOpen}
        onClose={addMealModal.close}
        onSubmit={handleAddModalSubmit}
        mealType={addMealModal.selectedMealType}
        mealIndex={addMealModal.selectedMealIndex}
        date={date}
        isLoading={m.meals.createMutation.isPending}
        error={m.meals.createMutation.isError
          ? '追加に失敗しました。/meal-items エンドポイントを確認してください。'
          : null
        }
      />
    </div>
  );
}
```

## 利点・効果

### 1. コードの簡潔性
- `handleAddClick`: 5行 → 2行（60%削減）
- 状態管理の重複コード除去
- イベントハンドラーの簡潔化

### 2. 責務分離の明確化
- モーダル状態管理の専用化
- ページロジックからUI状態を分離
- 各層の責務が明確

### 3. 再利用性の向上
- 他のページでも同じモーダルを簡単に使用可能
- モーダル状態管理の汎用化
- テストの独立性向上

### 4. 型安全性の確保
- TypeScript インターフェースによる厳密な型定義
- コンパイル時のエラー検出
- IDE支援の向上

### 5. 保守性の向上
- モーダルの状態管理が一箇所に集約
- 変更の影響範囲が限定的
- 新機能追加時の拡張性

## モーダル適用優先順位

### 完了済み
1. ✅ **Add Meal Modal** - 完了（2024-02-05）

### 次回適用予定（複雑度の低い順）
2. **Edit Meal Modal** - 類似パターン、比較的シンプル
   - `editingMealItem` 状態管理
   - `setEditingMealItem` 置き換え

3. **Meal Recommendation Detail Modal** - データ表示中心
   - `selectedRecommendation` 状態管理
   - `setSelectedRecommendation` 置き換え

4. **Nutrition Analysis Modal** - 複雑な状態管理
   - 既存Hook統合が必要
   - `nutritionDetailsData` と新Hook並行稼働

## 実装チェックリスト

### Hook作成段階
- [ ] `use{Modal}ModalState.ts` ファイル作成
- [ ] インターフェース定義（State + Actions + Model）
- [ ] `useState` による状態管理実装
- [ ] `useCallback` によるアクション実装
- [ ] JSDoc コメント追加

### Page統合段階
- [ ] Page Component での Hook import
- [ ] Hook インスタンス化
- [ ] 既存のインライン状態削除
- [ ] イベントハンドラーの簡潔化
- [ ] Modal Component Props 更新

### 検証段階
- [ ] TypeScript コンパイルエラー解消
- [ ] 機能動作確認
- [ ] UI/UX確認
- [ ] レグレッションテスト

## 注意事項

### 移行時の配慮
1. **段階的移行**: 一度に全てのモーダルを変更せず、一つずつ確実に
2. **既存機能保持**: 移行中も既存機能が正常に動作することを確認
3. **型安全性**: TypeScript型定義を厳密に定義し、コンパイル時エラーを防ぐ

### アーキテクチャ準拠
1. **Layer 2 責務**: モーダル状態管理のみに専念
2. **副作用回避**: useCallback を使用してパフォーマンス最適化
3. **インターフェース設計**: 将来の拡張性を考慮した設計

## 次回実装ガイドライン

次回のEdit Meal Modalリファクタリング時は、以下の手順で進める：

1. `useEditMealModalState.ts` 作成
2. `EditMealModalState` インターフェース定義
3. `isOpen`, `editingMealItem` 状態管理
4. `open(mealItem)`, `close()` アクション実装
5. TodayPageContent.tsx への統合
6. 既存状態の削除と置き換え
7. 動作確認とテスト

---

*最終更新: 2024-02-05*
*実装者: Claude Code Assistant*