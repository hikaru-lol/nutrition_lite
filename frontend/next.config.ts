import type { NextConfig } from 'next';

// const BACKEND_ORIGIN = process.env.BACKEND_ORIGIN ?? 'http://localhost:8000';
const BACKEND_ORIGIN = 'http://localhost:8000';

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${BACKEND_ORIGIN}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
