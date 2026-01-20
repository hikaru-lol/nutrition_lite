// export default function OnboardingTargetPage() {
//   return <div>Onboarding Target Page</div>;
// }

'use client';

import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card';
import { TargetCreationForm } from '@/modules/targets/ui/TargetCreationForm';

export default function OnboardingTargetPage() {
  const router = useRouter();

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-center">目標の設定</CardTitle>
        <CardDescription className="text-center">
          目指すゴールと活動レベルを設定してください。
          AIが最適な栄養バランスを提案します。
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TargetCreationForm
          onSuccess={() => {
            // 全て完了！メイン機能（食事リスト）へ
            router.push('/meals');
          }}
        />
      </CardContent>
    </Card>
  );
}
