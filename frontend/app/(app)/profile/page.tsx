// frontend/app/(app)/profile/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import {
  ProfileForm,
  type ProfileFormValues,
} from '@/components/profile/ProfileForm';
import {
  fetchProfile,
  upsertProfile,
  type ProfileResponseApi,
} from '@/lib/api/profile';
import { ApiError } from '@/lib/api/client';

export default function ProfilePage() {
  const router = useRouter();
  const [initialValues, setInitialValues] = useState<
    Partial<ProfileFormValues> | undefined
  >(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setServerError(null);

        const profile = await fetchProfile();
        if (cancelled) return;

        setInitialValues(mapApiToFormValues(profile));
      } catch (e: any) {
        if (e instanceof ApiError && e.status === 404) {
          // プロフィール未作成 → 空フォームとして扱う
          if (!cancelled) setInitialValues(undefined);
        } else {
          console.error('Failed to fetch profile', e);
          if (!cancelled) {
            setServerError(e?.message ?? 'プロフィールの取得に失敗しました。');
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSubmit = async (values: ProfileFormValues) => {
    try {
      setIsSubmitting(true);
      setServerError(null);

      const body = mapFormToApiRequest(values);
      await upsertProfile(body);

      // プロフィール編集の場合はそのままページに留まる or 軽いフィードバック
      // とりあえずリロードして最新を反映
      router.refresh();
    } catch (e: any) {
      console.error('Failed to save profile', e);
      setServerError(e?.message ?? 'プロフィールの保存に失敗しました。');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <PageHeader title="プロフィール" />
        <p className="text-sm text-slate-400">
          プロフィールを読み込んでいます...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="プロフィール"
        description="基本情報や1日の食事回数をいつでも見直すことができます。"
      />
      <ProfileForm
        initialValues={initialValues}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        serverError={serverError}
        submitLabel="保存する"
      />
    </div>
  );
}

// Onboarding側と同じ変換ロジック。
// 共通化したければ別ファイルに切り出してもOK。
function mapApiToFormValues(profile: ProfileResponseApi): ProfileFormValues {
  return {
    sex: profile.sex,
    birthdate: profile.birthdate,
    heightCm: profile.height_cm.toString(),
    weightKg: profile.weight_kg.toString(),
    mealsPerDay: profile.meals_per_day ? profile.meals_per_day.toString() : '3',
  };
}

function mapFormToApiRequest(values: ProfileFormValues) {
  return {
    sex: values.sex,
    birthdate: values.birthdate,
    height_cm: Number(values.heightCm),
    weight_kg: Number(values.weightKg),
    meals_per_day: Number(values.mealsPerDay),
  };
}
