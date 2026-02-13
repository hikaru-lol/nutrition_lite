import { NextRequest } from 'next/server';
import { backendUrl, proxyToBackend } from '@/shared/api/proxy';

export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    backendUrl('/nutrition/daily/report', req.nextUrl.search)
  );
}

export async function POST(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/nutrition/daily/report', ''));
}
