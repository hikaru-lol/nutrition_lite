// app/today/page.tsx (または該当のpage.tsx)
import { Suspense } from 'react';
import { TodayPage } from '@/modules/today/ui/TodayPage';
import { LoadingState } from '@/shared/ui/Status/LoadingState'; // 既存のローディングコンポーネントがあれば

export default function Page() {
  return (
    // 💡 ここでSuspenseバリアを張る
    <Suspense fallback={<LoadingState label="読み込み中..." />}>
      <TodayPage />
    </Suspense>
  );
}