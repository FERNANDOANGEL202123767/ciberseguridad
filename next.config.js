/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
      return [
        {
          source: '/static_assets/:path*',
          destination: 'http://192.168.0.44:8000/static_assets/:path*',
        },
        {
          source: '/captures/:path*',
          destination: 'http://192.168.0.44:8000/captures/:path*',
        },
        {
          source: '/public/:path*',
          destination: 'http://192.168.0.44:8000/public/:path*',
        },
      ];
    },
    allowedDevOrigins: [
      'http://localhost:3000',
      'http://127.0.0.1:3000',
      'http://192.168.0.44:3000',
      'http://192.168.0.44:8000',
    ],
  };
  
  module.exports = nextConfig;