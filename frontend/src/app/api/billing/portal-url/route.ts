import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

export async function GET(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/billing/portal-url'));
}
