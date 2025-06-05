/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    forceSwcTransforms: true // Force SWC transforms
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `connect-src \'self\' https://app-sicb.onrender.com;`
          },
        ]
      },
    ];
  }
}

module.exports = nextConfig 