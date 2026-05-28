/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // API requests are handled by src/app/api/[...path]/route.js
  // which proxies to BACKEND_URL (set in .env.local for dev, Vercel env for prod)
  // Local dev: set BACKEND_URL=http://localhost:8000 in frontend/.env.local
};

export default nextConfig;
