/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Lint is run separately in CI; don't block production builds on it.
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
