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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api/v1';

console.log('Mock handlers API_BASE_URL', API_BASE_URL);

// モックデータ
const mockUser: UserSummaryApi = {
  id: 'mock-user-id',
  email: 'test@example.com',
  name: 'テストユーザー',
  plan: 'free',
  trial_ends_at: null,
  has_profile: true,
  created_at: new Date().toISOString(),
};

const mockMealItems: MealItemResponse[] = [
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

const mockDailyReport: DailyNutritionReportResponse = {
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

const mockTargets: TargetResponseApi[] = [
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

const mockProfile: ProfileResponseApi = {
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

const mockRecommendation: RecommendationResponseApi = {
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

export const handlers = [
  // 認証関連
  http.get(`${API_BASE_URL}/auth/me`, () => {
    return HttpResponse.json<AuthUserResponse>({
      user: mockUser,
    });
  }),

  http.post(`${API_BASE_URL}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };
    // モックでは常に成功
    return HttpResponse.json<AuthUserResponse>({
      user: { ...mockUser, email: body.email },
    });
  }),

  http.post(`${API_BASE_URL}/auth/register`, async ({ request }) => {
    const body = (await request.json()) as {
      email: string;
      password: string;
      name?: string;
    };
    return HttpResponse.json<AuthUserResponse>({
      user: {
        ...mockUser,
        email: body.email,
        name: body.name ?? null,
      },
    });
  }),

  http.post(`${API_BASE_URL}/auth/logout`, () => {
    return HttpResponse.json({ ok: true });
  }),

  // 食事関連
  http.get(`${API_BASE_URL}/meal-items`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');

    return HttpResponse.json<MealItemListResponse>({
      items: mockMealItems.map((item) => ({
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
    return HttpResponse.json<MealItemResponse>(newItem, { status: 201 });
  }),

  http.patch(`${API_BASE_URL}/meal-items/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Partial<MealItemResponse>;
    const existingItem = mockMealItems.find((item) => item.id === params.id);

    if (!existingItem) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Meal item not found' } },
        { status: 404 }
      );
    }

    return HttpResponse.json<MealItemResponse>({
      ...existingItem,
      ...body,
    });
  }),

  http.delete(`${API_BASE_URL}/meal-items/:id`, ({ params }) => {
    const exists = mockMealItems.some((item) => item.id === params.id);
    if (!exists) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Meal item not found' } },
        { status: 404 }
      );
    }
    return new HttpResponse(null, { status: 204 });
  }),

  // 日次レポート関連
  http.get(`${API_BASE_URL}/nutrition/daily/report`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');

    return HttpResponse.json<DailyNutritionReportResponse>({
      ...mockDailyReport,
      date: date ?? mockDailyReport.date,
    });
  }),

  http.post(`${API_BASE_URL}/nutrition/daily/report`, async ({ request }) => {
    const body = (await request.json()) as { date: string };
    return HttpResponse.json<DailyNutritionReportResponse>({
      ...mockDailyReport,
      date: body.date,
    });
  }),

  // ターゲット関連
  http.get(`${API_BASE_URL}/targets`, () => {
    return HttpResponse.json<{ items: TargetResponseApi[] }>({
      items: mockTargets,
    });
  }),

  http.get(`${API_BASE_URL}/targets/active`, () => {
    const activeTarget = mockTargets.find((t) => t.is_active);
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
    return HttpResponse.json<TargetResponseApi>(newTarget, { status: 201 });
  }),

  http.post(`${API_BASE_URL}/targets/:id/activate`, ({ params }) => {
    const target = mockTargets.find((t) => t.id === params.id);
    if (!target) {
      return HttpResponse.json(
        { error: { code: 'NOT_FOUND', message: 'Target not found' } },
        { status: 404 }
      );
    }
    return HttpResponse.json<TargetResponseApi>({
      ...target,
      is_active: true,
    });
  }),

  // プロフィール関連
  http.get(`${API_BASE_URL}/profile/me`, () => {
    return HttpResponse.json<ProfileResponseApi>(mockProfile);
  }),

  http.put(`${API_BASE_URL}/profile/me`, async ({ request }) => {
    const body = (await request.json()) as ProfileRequestApi;
    return HttpResponse.json<ProfileResponseApi>({
      ...mockProfile,
      ...body,
      updated_at: new Date().toISOString(),
    });
  }),

  // 請求関連
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

  // レコメンデーション関連
  http.get(`${API_BASE_URL}/nutrition/recommendation/latest`, () => {
    return HttpResponse.json<RecommendationResponseApi>(mockRecommendation);
  }),

  http.get(`${API_BASE_URL}/nutrition/recommendation`, ({ request }) => {
    const url = new URL(request.url);
    const date = url.searchParams.get('date');

    return HttpResponse.json<RecommendationResponseApi>({
      ...mockRecommendation,
      generated_for_date: date ?? mockRecommendation.generated_for_date,
    });
  }),

  http.post(`${API_BASE_URL}/nutrition/recommendation`, async ({ request }) => {
    const body = (await request.json()) as { base_date: string };
    return HttpResponse.json<RecommendationResponseApi>({
      ...mockRecommendation,
      id: `rec-${Date.now()}`,
      generated_for_date: body.base_date,
      created_at: new Date().toISOString(),
    });
  }),
];
