import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    // TypeScript errors ko ignore karne ke liye
    ignoreBuildErrors: true,
  },
  eslint: {
    // ESLint errors/warnings ko ignore karne ke liye
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;