import type { NextConfig } from "next";

// Fail fast on Vercel if public API URL is missing (avoids baking localhost into the client bundle).
if (process.env.VERCEL && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error(
    'Missing NEXT_PUBLIC_API_URL. Set it in Vercel → Project → Settings → Environment Variables (e.g. https://your-api.example.com/api/v1).'
  );
}

const nextConfig: NextConfig = {
  // Standalone is for Docker/self-host only. Vercel uses its own output pipeline.
  ...(process.env.DOCKER_BUILD === "1" ? { output: "standalone" as const } : {}),
  poweredByHeader: false,
};

export default nextConfig;
