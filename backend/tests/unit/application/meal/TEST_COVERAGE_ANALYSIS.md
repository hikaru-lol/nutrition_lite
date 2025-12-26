# Meal UseCase ユニットテスト カバレッジ分析

## 現在のテスト状況

### ✅ カバーされているテストケース

#### CreateFoodEntryUseCase

- ✅ main meal with amount_value and unit（正常系）
- ✅ snack with serving_count only（正常系）
- ✅ InvalidMealTypeError（異常系）
- ✅ InvalidFoodAmountError - 量が指定されていない場合（異常系）

#### UpdateFoodEntryUseCase

- ✅ 正常系の更新（全フィールド更新）
- ✅ FoodEntryNotFoundError（異常系）
- ✅ InvalidMealTypeError（異常系）

#### DeleteFoodEntryUseCase

- ✅ 正常系の削除
- ✅ FoodEntryNotFoundError（異常系）

#### ListFoodEntriesByDateUseCase

- ✅ 正常系のリスト取得（ユーザー・日付フィルタリング）

---

## ❌ 不足しているテストケース

### CreateFoodEntryUseCase

1. **InvalidMealIndexError のテスト**

   - `meal_type=main` で `meal_index=None` の場合
   - `meal_type=main` で `meal_index < 1` の場合
   - `meal_type=snack` で `meal_index` が None 以外の場合

2. **InvalidFoodAmountError の追加テスト**

   - `amount_value` のみ指定（`amount_unit` なし）
   - `amount_unit` のみ指定（`amount_value` なし）
   - `amount_value <= 0` の場合
   - `serving_count <= 0` の場合

3. **エッジケース**
   - `amount_value` と `serving_count` の両方を指定した場合（正常系だが、テストされていない）

### UpdateFoodEntryUseCase

1. **InvalidMealIndexError のテスト**

   - `meal_type=main` で `meal_index=None` に更新する場合
   - `meal_type=main` で `meal_index < 1` に更新する場合
   - `meal_type=snack` で `meal_index` を None 以外に更新する場合

2. **InvalidFoodAmountError のテスト**

   - `amount_value` のみ指定（`amount_unit` なし）
   - `amount_unit` のみ指定（`amount_value` なし）
   - `amount_value <= 0` の場合
   - `serving_count <= 0` の場合
   - 量が指定されていない場合

3. **セキュリティテスト**
   - 他のユーザーのエントリを更新しようとした場合（`FoodEntryNotFoundError` が発生することを確認）

### DeleteFoodEntryUseCase

1. **セキュリティテスト**

   - 他のユーザーのエントリを削除しようとした場合（`FoodEntryNotFoundError` が発生することを確認）

2. **冪等性テスト**
   - 既に削除されたエントリを再度削除しようとした場合（エラーにならないことを確認）

### ListFoodEntriesByDateUseCase

1. **エッジケース**
   - エントリが存在しない日付の場合（空のリストが返ることを確認）
   - 削除されたエントリが含まれないことを確認（既にテストされているが、明示的にテストすべき）

---

## 推奨事項

### 優先度: 高

1. **セキュリティテストの追加**

   - 他のユーザーのエントリにアクセスできないことを確認するテストは重要
   - Update, Delete で追加が必要

2. **InvalidMealIndexError のテスト**

   - ドメインの不変条件をテストする重要なケース
   - Create, Update で追加が必要

3. **InvalidFoodAmountError の追加テスト**
   - 量指定のバリデーションは重要なビジネスロジック
   - Create, Update で追加が必要

### 優先度: 中

4. **エッジケースのテスト**

   - 空のリスト、負の値、ゼロ値などのエッジケース

5. **冪等性テスト**
   - Delete の冪等性は実装されているが、テストで確認すべき

---

## テストの品質評価

### 良い点

- ✅ 正常系と主要な異常系がカバーされている
- ✅ Fake リポジトリを使用して適切に依存関係が分離されている
- ✅ UoW パターンが正しく使用されている（修正後）
- ✅ テストが独立しており、互いに影響しない

### 改善点

- ❌ セキュリティテスト（他ユーザーアクセス）が不足
- ❌ ドメインのバリデーションエラーのテストが不完全
- ❌ エッジケースのテストが不足
- ❌ テストの説明（docstring）が不足している場合がある

---

## 結論

現在のテストは基本的な正常系と主要な異常系をカバーしていますが、以下の点で改善の余地があります：

1. **セキュリティテスト**: 他ユーザーのエントリへのアクセス制御のテストが不足
2. **バリデーションテスト**: `InvalidMealIndexError` と `InvalidFoodAmountError` の一部のケースが未テスト
3. **エッジケース**: 負の値、ゼロ値、空のリストなどのエッジケース

ユニットテストとして**基本的には十分**ですが、**セキュリティとバリデーションのテストを追加することで、より堅牢なテストスイートになります**。
