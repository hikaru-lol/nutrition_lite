// frontend/lib/mocks/handlers.ts
import { http, HttpResponse } from 'msw';
import type { UserSummaryApi, AuthUserResponse } from '@/lib/api/auth';
import type { MealItemListResponse, MealItemResponse } from '@/lib/api/meals';
import type { DailyNutritionReportResponse } from '@/lib/api/dailyReport';
import type {
  // TargetListResponseApi,
  TargetResponseApi,
} from '@/lib/api/targets';
import type { ProfileResponseApi, ProfileRequestApi } from '@/lib/api/profile';
import type {
  CheckoutSessionResponse,
  BillingPortalResponse,
} from '@/lib/api/billing';
import type { RecommendationResponseApi } from '@/lib/api/recommendation';
import type {
  MealNutritionSummaryApi,
  DailyNutritionSummaryApi,
  MealAndDailyNutritionResponse,
} from '@/lib/api/nutrition';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api/v1';

console.log('Mock handlers API_BASE_URL', API_BASE_URL);

/* ================================
 * 認証 / ユーザー（インメモリ）
 * ================================ */

// 初期ユーザーデータ
const initialUser: UserSummaryApi = {
  id: 'mock-user-id',
  email: 'test@example.com',
  name: 'テストユーザー',
  plan: 'free',
  trial_ends_at: null,
  has_profile: true,
  created_at: new Date().toISOString(),
};

// インメモリ「現在のユーザー」
let currentUser: UserSummaryApi = { ...initialUser };

/* ================================
 * 食事（インメモリ）
 * ================================ */

// 初期データ
const initialMealItems: MealItemResponse[] = [
  {
    id: 'meal-1',
    date: new Date().toISOString().split('T')[0],
    meal_type: 'main',
    meal_index: 1,
    name: '白米',
    amount_value: 150,
    amount_unit: 'g',
    serving_count: 1,
    note: null,
  },
  {
    id: 'meal-2',
    date: new Date().toISOString().split('T')[0],
    meal_type: 'main',
    meal_index: 1,
    name: '味噌汁',
    amount_value: 200,
    amount_unit: 'ml',
    serving_count: 1,
    note: null,
  },
];

// インメモリ「食事DB」
const mealItems: MealItemResponse[] = [...initialMealItems];

/* ================================
 * 日次レポート（インメモリ）
 * ================================ */

// ひとつのレポートの初期値
const initialDailyReport: DailyNutritionReportResponse = {
  date: new Date().toISOString().split('T')[0],
  summary: '本日の栄養バランスは良好です。',
  good_points: ['タンパク質の摂取量が適切です', '野菜をしっかり摂れています'],
  improvement_points: [
    '水分補給をもう少し意識しましょう',
    '食物繊維の摂取量を増やすと良いでしょう',
  ],
  tomorrow_focus: ['朝食に野菜を追加', '水分を2L以上摂取'],
  created_at: new Date().toISOString(),
};

// 日付ごとのレポートを保持（超ざっくりインメモリDB）
const dailyReports: Record<string, DailyNutritionReportResponse> = {
  [initialDailyReport.date]: initialDailyReport,
};

/* ================================
 * ターゲット（インメモリ）
 * ================================ */

const initialTargets: TargetResponseApi[] = [
  {
    id: 'target-1',
    user_id: 'mock-user-id',
    title: '健康維持',
    goal_type: 'maintain',
    goal_description: '現在の体重を維持しながら健康を保つ',
    activity_level: 'normal',
    is_active: true,
    nutrients: [
      {
        code: 'carbohydrate',
        amount: 250,
        unit: 'g',
        source: 'llm',
      },
      {
        code: 'protein',
        amount: 100,
        unit: 'g',
        source: 'llm',
      },
      {
        code: 'fat',
        amount: 60,
        unit: 'g',
        source: 'llm',
      },
    ],
    llm_rationale: '標準的な活動レベルの成人に適した栄養目標です',
    disclaimer: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// インメモリ「ターゲットDB」
let targets: TargetResponseApi[] = [...initialTargets];

/* ================================
 * プロフィール（インメモリ）
 * ================================ */

const initialProfile: ProfileResponseApi = {
  user_id: 'mock-user-id',
  sex: 'male',
  birthdate: '1990-01-01',
  height_cm: 170,
  weight_kg: 70,
  meals_per_day: 3,
  image_id: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

let currentProfile: ProfileResponseApi = { ...initialProfile };

/* ================================
 * レコメンデーション（インメモリ）
 * ================================ */

const initialRecommendation: RecommendationResponseApi = {
  id: 'rec-1',
  user_id: 'mock-user-id',
  generated_for_date: new Date().toISOString().split('T')[0],
  body: '本日の食事バランスを考慮すると、夕食にタンパク質を追加することをお勧めします。',
  tips: [
    '朝食に野菜を追加しましょう',
    '水分をこまめに摂取してください',
    '間食はナッツ類がおすすめです',
  ],
  created_at: new Date().toISOString(),
};

// インメモリ「レコメンDB」
const recommendations: RecommendationResponseApi[] = [initialRecommendation];

/* ================================
 * 栄養計算（擬似）
 * ================================ */

function computeMockNutrients(
  entries: MealItemResponse[]
): MealNutritionSummaryApi[] {
  // amount_value を適当に PFC に割り振る簡易ロジック
  let totalAmount = 0;
  for (const e of entries) {
    if (typeof e.amount_value === 'number') {
      totalAmount += e.amount_value;
    }
  }

  // 適当な比率で割り振る（例：炭水化物50%, タンパク質30%, 脂質20%)
  const energy = totalAmount * 2; // 適当な "kcal" っぽい値
  const carb = totalAmount * 0.5;
  const protein = totalAmount * 0.3;
  const fat = totalAmount * 0.2;

  const nutrients: NutritionNutrientIntakeApi[] = [
    {
      code: 'carbohydrate',
      amount: Math.round(carb),
      unit: 'g',
      source: 'llm',
    },
    {
      code: 'protein',
      amount: Math.round(protein),
      unit: 'g',
      source: 'llm',
    },
    {
      code: 'fat',
      amount: Math.round(fat),
      unit: 'g',
      source: 'llm',
    },
    // 必要なら他の栄養素も適当に追加
  ];

  return nutrients;
}

export const handlers = [
  /* ========== Auth ========== */

  http.get(`${API_BASE_URL}/auth/me`, () => {
    return HttpResponse.json<AuthUserResponse>({
      user: currentUser,
    });
  }),

  http.post(`${API_BASE_URL}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };

    currentUser = {
      ...currentUser,
      email: body.email,
    };

    return HttpResponse.json<AuthUserResponse>({
      user: currentUser,
    });
  }),

  http.post(`${API_BASE_URL}/auth/register`, async ({ request }) => {
    const body = (await request.json()) as {
      email: string;
      password: string;
      name?: string;
    };

    currentUser = {
      ...currentUser,
      email: body.email,
      name: body.name ?? null,
    };

    return HttpResponse.json<AuthUserResponse>({
      user: currentUser,
    });
  }),

  http.post(`${API_BASE_URL}/auth/logout`, () => {
    // とりあえず何もしないで OK を返す
    return HttpResponse.json({ ok: true });
  }),

  /* ========== Meal Items ========== */

  http.get(`${API_BASE_URL}/meal-items`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');

    return HttpResponse.json<MealItemListResponse>({
      items: mealItems.map((item) => ({
        ...item,
        date: date ?? item.date,
      })),
    });
  }),

  http.post(`${API_BASE_URL}/meal-items`, async ({ request }) => {
    const body = (await request.json()) as Partial<MealItemResponse>;
    const newItem: MealItemResponse = {
      id: `meal-${Date.now()}`,
      date: body.date ?? new Date().toISOString().split('T')[0],
      meal_type: body.meal_type ?? 'main',
      meal_index: body.meal_index ?? null,
      name: body.name ?? '新しい食事',
      amount_value: body.amount_value ?? null,
      amount_unit: body.amount_unit ?? null,
      serving_count: body.serving_count ?? null,
      note: body.note ?? null,
    };

    mealItems.push(newItem);

    return HttpResponse.json<MealItemResponse>(newItem, { status: 201 });
  }),

  http.patch(`${API_BASE_URL}/meal-items/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Partial<MealItemResponse>;
    const index = mealItems.findIndex((item) => item.id === params.id);

    if (index === -1) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Meal item not found' } },
        { status: 404 }
      );
    }

    const updated: MealItemResponse = {
      ...mealItems[index],
      ...body,
    };

    mealItems[index] = updated;

    return HttpResponse.json<MealItemResponse>(updated);
  }),

  http.delete(`${API_BASE_URL}/meal-items/:id`, ({ params }) => {
    const index = mealItems.findIndex((item) => item.id === params.id);

    if (index === -1) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Meal item not found' } },
        { status: 404 }
      );
    }

    mealItems.splice(index, 1);

    return new HttpResponse(null, { status: 204 });
  }),

  /* ========== Daily Nutrition Report ========== */

  http.get(`${API_BASE_URL}/nutrition/daily/report`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date') ?? initialDailyReport.date;

    const report =
      dailyReports[date] ??
      ({
        ...initialDailyReport,
        date,
      } satisfies DailyNutritionReportResponse);

    return HttpResponse.json<DailyNutritionReportResponse>(report);
  }),

  http.post(`${API_BASE_URL}/nutrition/daily/report`, async ({ request }) => {
    const body = (await request.json()) as { date: string };
    const date = body.date;

    const newReport: DailyNutritionReportResponse = {
      ...initialDailyReport,
      date,
      created_at: new Date().toISOString(),
    };

    dailyReports[date] = newReport;

    return HttpResponse.json<DailyNutritionReportResponse>(newReport);
  }),

  /* ========== Targets ========== */

  http.get(`${API_BASE_URL}/targets`, () => {
    return HttpResponse.json<{ items: TargetResponseApi[] }>({
      items: targets,
    });
  }),

  http.get(`${API_BASE_URL}/targets/active`, () => {
    const activeTarget = targets.find((t) => t.is_active);
    if (!activeTarget) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Active target not found' } },
        { status: 404 }
      );
    }
    return HttpResponse.json<TargetResponseApi>(activeTarget);
  }),

  http.post(`${API_BASE_URL}/targets`, async ({ request }) => {
    const body = (await request.json()) as Partial<TargetResponseApi>;
    const newTarget: TargetResponseApi = {
      id: `target-${Date.now()}`,
      user_id: 'mock-user-id',
      title: body.title ?? '新しいターゲット',
      goal_type: body.goal_type ?? 'maintain',
      goal_description: body.goal_description ?? null,
      activity_level: body.activity_level ?? 'normal',
      is_active: false,
      nutrients: body.nutrients ?? [],
      llm_rationale: null,
      disclaimer: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    targets.push(newTarget);

    return HttpResponse.json<TargetResponseApi>(newTarget, { status: 201 });
  }),

  http.post(`${API_BASE_URL}/targets/:id/activate`, ({ params }) => {
    const index = targets.findIndex((t) => t.id === params.id);
    if (index === -1) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Target not found' } },
        { status: 404 }
      );
    }

    // シンプルにそのターゲットだけ active にする例
    targets = targets.map((t, i) => ({
      ...t,
      is_active: i === index,
    }));

    return HttpResponse.json<TargetResponseApi>(targets[index]);
  }),

  /* ========== Profile ========== */

  http.get(`${API_BASE_URL}/profile/me`, () => {
    return HttpResponse.json<ProfileResponseApi>(currentProfile);
  }),

  http.put(`${API_BASE_URL}/profile/me`, async ({ request }) => {
    const body = (await request.json()) as ProfileRequestApi;

    currentProfile = {
      ...currentProfile,
      ...body,
      updated_at: new Date().toISOString(),
    };

    return HttpResponse.json<ProfileResponseApi>(currentProfile);
  }),

  /* ========== Billing（状態なしでOK） ========== */

  http.post(`${API_BASE_URL}/billing/checkout-session`, () => {
    return HttpResponse.json<CheckoutSessionResponse>({
      checkout_url: 'https://checkout.stripe.com/mock-session',
    });
  }),

  http.get(`${API_BASE_URL}/billing/portal-url`, () => {
    return HttpResponse.json<BillingPortalResponse>({
      portal_url: 'https://billing.stripe.com/mock-portal',
    });
  }),

  /* ========== Recommendation ========== */

  http.get(`${API_BASE_URL}/nutrition/recommendation/latest`, () => {
    // 一番新しいもの（created_at 降順）を返す
    const latest =
      recommendations
        .slice()
        .sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )[0] ?? initialRecommendation;

    return HttpResponse.json<RecommendationResponseApi>(latest);
  }),

  http.get(`${API_BASE_URL}/nutrition/recommendation`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');

    if (!date) {
      // date がないときは latest と同じ扱い
      const latest =
        recommendations
          .slice()
          .sort(
            (a, b) =>
              new Date(b.created_at).getTime() -
              new Date(a.created_at).getTime()
          )[0] ?? initialRecommendation;

      return HttpResponse.json<RecommendationResponseApi>(latest);
    }

    const found =
      recommendations.find((rec) => rec.generated_for_date === date) ??
      ({
        ...initialRecommendation,
        generated_for_date: date,
      } satisfies RecommendationResponseApi);

    return HttpResponse.json<RecommendationResponseApi>(found);
  }),

  http.post(`${API_BASE_URL}/nutrition/recommendation`, async ({ request }) => {
    const body = (await request.json()) as { base_date: string };

    const newRec: RecommendationResponseApi = {
      ...initialRecommendation,
      id: `rec-${Date.now()}`,
      generated_for_date: body.base_date,
      created_at: new Date().toISOString(),
    };

    recommendations.push(newRec);

    return HttpResponse.json<RecommendationResponseApi>(newRec);
  }),

  /* ========== Daily Meal Nutrition (/nutrition/meal) ========== */

  http.get(`${API_BASE_URL}/nutrition/meal`, ({ request }) => {
    const url = new URL(request.url);
    const date =
      url.searchParams.get('date') ?? new Date().toISOString().split('T')[0];
    const mealType =
      (url.searchParams.get('meal_type') as 'main' | 'snack') ?? 'main';
    const mealIndexParam = url.searchParams.get('meal_index');
    const mealIndex =
      mealType === 'main' && mealIndexParam ? Number(mealIndexParam) : null;

    // 対象ミールに紐づく FoodEntry を抽出
    const mealEntries = mealItems.filter((item) => {
      if (item.date !== date) return false;
      if (item.meal_type !== mealType) return false;
      if (mealType === 'main') {
        return item.meal_index === mealIndex;
      }
      // snack のときは meal_index は見ない
      return item.meal_type === 'snack';
    });

    // その日の全 FoodEntry から Daily 用も作る
    const dailyEntries = mealItems.filter((item) => item.date === date);

    // めちゃくちゃ簡易な擬似計算（実際のロジックはバックエンド側に任せる）
    const mealNutrients = computeMockNutrients(mealEntries);
    const dailyNutrients = computeMockNutrients(dailyEntries);

    const mealSummary: MealNutritionSummaryApi = {
      id: `meal-nut-${mealType}-${mealIndex ?? 'snack'}`,
      date,
      meal_type: mealType,
      meal_index: mealIndex,
      nutrients: mealNutrients,
      generated_at: new Date().toISOString(),
    };

    const dailySummary: DailyNutritionSummaryApi = {
      id: `daily-nut-${date}`,
      date,
      nutrients: dailyNutrients,
      generated_at: new Date().toISOString(),
    };

    const response: MealAndDailyNutritionResponse = {
      meal: mealSummary,
      daily: dailySummary,
    };

    return HttpResponse.json<MealAndDailyNutritionResponse>(response);
  }),
];
