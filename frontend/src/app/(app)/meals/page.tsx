import { MealList } from '@/modules/meals/ui/MealList';

export default function MealsPage() {
  return (
    // Rule B: Pageは「家具（コンポーネント）の配置」と「幅の制限」を担当する
    <div className="container mx-auto max-w-md px-4 py-8">
      {/* ヘッダー部分の配置 */}
      <div className="mb-6 space-y-1">
        <h1 className="text-2xl font-bold text-gray-900">食事管理</h1>
        <p className="text-sm text-gray-500">
          日々の食事を記録して、栄養バランスを整えましょう。
        </p>
      </div>

      {/* メイン機能（リスト＋追加ボタン）の配置 */}
      <MealList />
    </div>
  );
}
