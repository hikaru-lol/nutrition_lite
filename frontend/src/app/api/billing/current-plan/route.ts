import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

export async function GET(req: NextRequest) {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('ACCESS_TOKEN')?.value;

    if (!accessToken) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // 新しい billing/current-plan エンドポイントを使用
    const planResponse = await fetch(`${BACKEND}${PREFIX}/billing/current-plan`, {
      headers: {
        'Cookie': `ACCESS_TOKEN=${accessToken}`,
      },
    });

    if (!planResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch plan info' },
        { status: planResponse.status }
      );
    }

    const planData = await planResponse.json();

    // レスポンス形式をフロントエンドが期待する形に合わせる
    const planInfo = {
      user_plan: planData.user_plan,
      subscription_status: 'none', // TODO: 将来的にBillingAccountから取得
      is_trial_active: planData.is_trial_active,
      trial_ends_at: planData.trial_ends_at,
      subscription_id: null, // TODO: 将来的に実装
      customer_id: null, // TODO: 将来的に実装
    };

    return NextResponse.json(planInfo);
  } catch (error) {
    console.error('Current plan API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}