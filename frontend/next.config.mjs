/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://sentinelbrief-backend.onrender.com/api/:path*',
      },
    ];
  },
};

export default nextConfig;
