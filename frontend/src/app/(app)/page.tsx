// import { TodayPage } from '@/components/today/TodayPage';

// export default function Page() {
//   return <TodayPage />;
// }

'use client';

import Link from 'next/link';
import { NutritionSummary } from '@/modules/today/ui/NutritionSummary';
import { MealList } from '@/modules/meals/ui/MealList';
import { Button } from '@/shared/ui/button';

export default function DashboardPage() {
  return (
    // Rule B: コンポーネントの配置と余白管理
    <div className="container mx-auto max-w-md space-y-8 px-4 py-8">
      {/* 1. ダッシュボードセクション */}
      <section>
        <h2 className="mb-4 text-xl font-bold text-gray-900">
          Today's Progress
        </h2>
        <NutritionSummary />
      </section>

      {/* 2. 食事記録セクション */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Meals</h2>
          <Button variant="link" asChild className="text-blue-600">
            <Link href="/meals">詳細を見る</Link>
          </Button>
        </div>

        {/* ここにリストを直接置くことで、トップ画面からすぐ編集可能にする */}
        <MealList />
      </section>
    </div>
  );
}
