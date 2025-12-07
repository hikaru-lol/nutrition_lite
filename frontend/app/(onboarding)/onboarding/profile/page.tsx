'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ProfileForm,
  type ProfileFormValues,
} from '@/components/profile/ProfileForm';
// import { fetchProfile, upsertProfile } from "@/lib/api/profile";
// import { fetchMe } from "@/lib/api/auth";

export default function OnboardingProfilePage() {
  const router = useRouter();
  const [initialValues, setInitialValues] = useState<
    Partial<ProfileFormValues> | undefined
  >(undefined);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // 初期表示時に /profile を読みに行く（あればプリセット）
  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true);
        setServerError(null);
        // TODO: 実際のAPI呼び出しに置き換え
        // const profile = await fetchProfile();
        // if (profile) {
        //   setInitialValues({
        //     sex: profile.sex,
        //     birthdate: profile.birthdate ?? "",
        //     heightCm: profile.height_cm?.toString() ?? "",
        //     weightKg: profile.weight_kg?.toString() ?? "",
        //     mealsPerDay: profile.meals_per_day.toString(),
        //   });
        // }
      } catch (e: any) {
        setServerError(e?.message ?? 'プロフィールの取得に失敗しました。');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleSubmit = async (values: ProfileFormValues) => {
    try {
      setIsSubmitting(true);
      setServerError(null);

      // TODO: 実際のAPI用に整形して送信
      // await upsertProfile({
      //   sex: values.sex,
      //   birthdate: values.birthdate || null,
      //   height_cm: values.heightCm ? Number(values.heightCm) : null,
      //   weight_kg: values.weightKg ? Number(values.weightKg) : null,
      //   meals_per_day: Number(values.mealsPerDay),
      // });

      // const me = await fetchMe();
      // if (me.hasProfile) {
      //   router.push("/");
      // } else {
      //   router.push("/");
      // }

      // ひとまずダミーでトップに遷移
      router.push('/');
    } catch (e: any) {
      setServerError(e?.message ?? 'プロフィールの保存に失敗しました。');
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
