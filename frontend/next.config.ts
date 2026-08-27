import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone is for Docker/self-host only. Vercel uses its own output pipeline.
  ...(process.env.DOCKER_BUILD === "1" ? { output: "standalone" as const } : {}),
  poweredByHeader: false,
};

export default nextConfig;
