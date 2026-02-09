/**
 * 食事グループ化ユーティリティ
 *
 * 責務:
 * - 食事アイテムをメイン食事と間食にグループ化
 * - メイン食事を連番でソート
 * - 純粋関数（副作用なし）
 */

import type { MealItem } from '../contract/mealContract';

export interface GroupedMeals {
  main: Array<{ index: number; items: MealItem[] }>;
  snacks: MealItem[];
}

/**
 * 食事アイテムをメイン食事と間食にグループ化
 *
 * @param mealItems - 食事アイテム一覧
 * @param mealsPerDay - 1日の食事回数
 * @returns グループ化された食事データ
 */
export function groupMealsByType(
  mealItems: readonly MealItem[],
  mealsPerDay: number
): GroupedMeals {
  const mainMeals: { [key: number]: MealItem[] } = {};
  const snacks: MealItem[] = [];

  // 食事タイプごとに分類
  mealItems.forEach(item => {
    if (item.meal_type === 'main') {
      const index = item.meal_index ?? 1;
      if (!mainMeals[index]) {
        mainMeals[index] = [];
      }
      mainMeals[index].push(item);
    } else {
      snacks.push(item);
    }
  });

  // メイン食事を連番で配列に変換
  const mainArray: Array<{ index: number; items: MealItem[] }> = [];
  for (let i = 1; i <= mealsPerDay; i++) {
    mainArray.push({
      index: i,
      items: mainMeals[i] || []
    });
  }

  return { main: mainArray, snacks };
}
