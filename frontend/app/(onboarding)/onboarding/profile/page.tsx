// frontend/app/(onboarding)/onboarding/profile/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
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

export default function OnboardingProfilePage() {
  const router = useRouter();
  const [initialValues, setInitialValues] = useState<
    Partial<ProfileFormValues> | undefined
  >(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // 初期ロードで /profile/me を取得（あればフォームに反映）
  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setServerError(null);

        const profile = await fetchProfile();
        if (cancelled) return;

        setInitialValues(mapApiToFormValues(profile));
      } catch (e: unknown) {
        if (e instanceof ApiError && e.status === 404) {
          // プロフィール未作成 → initialValues は undefined のまま
          if (!cancelled) setInitialValues(undefined);
        } else {
          console.error('Failed to fetch profile', e);
          if (!cancelled) {
            const message =
              e instanceof Error
                ? e.message
                : 'プロフィールの取得に失敗しました。';
            setServerError(message);
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

      // フォーム値 → API リクエスト形式に変換
      const body = mapFormToApiRequest(values);
      await upsertProfile(body);

      // バックエンド側で has_profile が true になる前提なので、
      // ここではそのまま Today に飛ばしてOK
      router.push('/');
    } catch (e: unknown) {
      console.error('Failed to save profile', e);
      const message =
        e instanceof Error ? e.message : 'プロフィールの保存に失敗しました。';
      setServerError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <p className="text-sm text-slate-400">
        プロフィールを読み込んでいます...
      </p>
    );
  }

  return (
    <ProfileForm
      initialValues={initialValues}
      onSubmit={handleSubmit}
      isSubmitting={isSubmitting}
      serverError={serverError}
      submitLabel="保存してはじめる"
    />
  );
}

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
