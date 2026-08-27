"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/auth/session";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const restore = useAuthStore((s) => s.restore);

  useEffect(() => {
    restore();
  }, [restore]);

  return <>{children}</>;
}
