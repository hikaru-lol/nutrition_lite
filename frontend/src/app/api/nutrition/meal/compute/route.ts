import { proxyToBackend } from '@/shared/api/proxy';
import { NextRequest } from 'next/server';

const BACKEND = process.env.BACKEND_INTERNAL_ORIGIN ?? 'http://127.0.0.1:8000';
const PREFIX = '/api/v1';

export async function POST(req: NextRequest) {
  return proxyToBackend(
    req,
    `${BACKEND}${PREFIX}/nutrition/meal/compute${req.nextUrl.search}`
  );
}