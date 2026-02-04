/**
 * useTodayProfile - プロフィール管理専用フック（TodayPage特化）
 *
 * 責務:
 * - TodayPageで必要なプロフィール情報の取得
 * - 1日の食事回数等の設定値管理
 * - プロフィール関連の軽量データアクセス
 */

'use client';

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';

import { todayQueryKeys } from '../lib/queryKeys';
import type { TodayProfileModel } from '../types/todayTypes';
import { fetchProfile } from '@/modules/profile/api/profileClient';

// ========================================
// Main Hook
// ========================================

export function useTodayProfile(): TodayProfileModel {
  // ========================================
  // Data Fetching
  // ========================================

  // プロフィール情報取得
  const profileQuery = useQuery({
    queryKey: todayQueryKeys.profile(),
    queryFn: fetchProfile,
    staleTime: 1000 * 60 * 10, // 10分間キャッシュ
    retry: false,
  });

  // ========================================
  // Computed Values
  // ========================================

  // 1日の食事回数（デフォルト値との統合）
  const mealsPerDay = useMemo(() => {
    return profileQuery.data?.meals_per_day ?? 3; // デフォルト: 3食
  }, [profileQuery.data?.meals_per_day]);

  // ========================================
  // Return Value
  // ========================================

  return {
    // State
    profile: profileQuery.data ?? null,
    mealsPerDay,
    isLoading: profileQuery.isLoading,
    isError: profileQuery.isError,
  };
}

// ========================================
// 軽量版Hook（設定値のみ）
// ========================================

/**
 * TodayPageで必要な設定値のみを取得する超軽量フック
 */
export function useTodaySettings() {
  const { mealsPerDay, isLoading } = useTodayProfile();

  return {
    mealsPerDay,
    isLoading,
  };
}

// ========================================
// ユーティリティHook
// ========================================

/**
 * ユーザーの栄養目標設定状況を確認
 */
export function useProfileCompletionStatus() {
  const { profile, isLoading } = useTodayProfile();

  const completionStatus = useMemo(() => {
    if (!profile || isLoading) {
      return {
        isComplete: false,
        missingFields: [],
        completionPercentage: 0,
      };
    }

    const requiredFields = [
      'height',
      'weight',
      'age',
      'gender',
      'activity_level',
      'meals_per_day',
    ];

    const filledFields = requiredFields.filter(field => {
      const value = profile[field as keyof typeof profile];
      return value !== null && value !== undefined && value !== '';
    });

    const missingFields = requiredFields.filter(field => {
      const value = profile[field as keyof typeof profile];
      return value === null || value === undefined || value === '';
    });

    const completionPercentage = Math.round(
      (filledFields.length / requiredFields.length) * 100
    );

    return {
      isComplete: missingFields.length === 0,
      missingFields,
      completionPercentage,
      filledFields: filledFields.length,
      totalFields: requiredFields.length,
    };
  }, [profile, isLoading]);

  return completionStatus;
}

// ========================================
// Profile Helper Functions
// ========================================

/**
 * BMIを計算
 */
export function calculateBMI(height: number, weight: number): number {
  if (height <= 0 || weight <= 0) return 0;
  const heightInMeters = height / 100;
  return Math.round((weight / (heightInMeters * heightInMeters)) * 10) / 10;
}

/**
 * BMIカテゴリを取得
 */
export function getBMICategory(bmi: number): {
  category: string;
  status: 'underweight' | 'normal' | 'overweight' | 'obese';
  color: string;
} {
  if (bmi < 18.5) {
    return {
      category: '低体重',
      status: 'underweight',
      color: 'text-blue-500',
    };
  }
  if (bmi < 25) {
    return {
      category: '標準体重',
      status: 'normal',
      color: 'text-green-500',
    };
  }
  if (bmi < 30) {
    return {
      category: '肥満（1度）',
      status: 'overweight',
      color: 'text-yellow-500',
    };
  }
  return {
    category: '肥満（2度以上）',
    status: 'obese',
    color: 'text-red-500',
  };
}

/**
 * 基礎代謝量を計算（Harris-Benedict式）
 */
export function calculateBMR(
  height: number,
  weight: number,
  age: number,
  gender: 'male' | 'female'
): number {
  if (height <= 0 || weight <= 0 || age <= 0) return 0;

  if (gender === 'male') {
    return Math.round(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age));
  } else {
    return Math.round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age));
  }
}

/**
 * 活動レベル係数を取得
 */
export function getActivityMultiplier(activityLevel: string): number {
  switch (activityLevel) {
    case 'sedentary':     return 1.2;   // 座りがち
    case 'lightly_active': return 1.375; // 軽度の活動
    case 'moderately_active': return 1.55; // 中程度の活動
    case 'very_active':   return 1.725;  // 高い活動
    case 'extra_active':  return 1.9;    // 非常に高い活動
    default:              return 1.375;  // デフォルト
  }
}

/**
 * 1日の推奨カロリーを計算
 */
export function calculateDailyCalories(
  height: number,
  weight: number,
  age: number,
  gender: 'male' | 'female',
  activityLevel: string
): number {
  const bmr = calculateBMR(height, weight, age, gender);
  const multiplier = getActivityMultiplier(activityLevel);
  return Math.round(bmr * multiplier);
}