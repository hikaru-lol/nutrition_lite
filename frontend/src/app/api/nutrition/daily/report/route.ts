import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/shared/api/proxy';

const BACKEND_INTERNAL_ORIGIN =
  process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const BACKEND_API_PREFIX = process.env.BACKEND_API_PREFIX ?? '/api/v1';

function backendUrl(path: string, search: string) {
  return `${BACKEND_INTERNAL_ORIGIN}${BACKEND_API_PREFIX}${path}${search}`;
}

export async function GET(req: NextRequest) {
  return proxyToBackend(
    req,
    backendUrl('/nutrition/daily/report', req.nextUrl.search)
  );
}

export async function POST(req: NextRequest) {
  return proxyToBackend(req, backendUrl('/nutrition/daily/report', ''));
}
