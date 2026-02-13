import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

export async function POST(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/billing/checkout-session'));
}
