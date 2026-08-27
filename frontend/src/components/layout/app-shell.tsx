"use client";

import { useAuthStore } from "@/lib/auth/session";
import { useRouter } from "next/navigation";
import { useEffect, useState, createContext, useContext } from "react";
import { cn } from "@/lib/utils";

/* ─── Sidebar width context ─── */
interface SidebarContextValue {
  collapsed: boolean;
  toggle: () => void;
}
const SidebarContext = createContext<SidebarContextValue>({
  collapsed: false,
  toggle: () => {},
});

export function useSidebar() {
  return useContext(SidebarContext);
}

/* ─── AppShell ─── */
interface AppShellProps {
  children: React.ReactNode;
  className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <AppShellSkeleton />;
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <SidebarContext.Provider
      value={{ collapsed, toggle: () => setCollapsed((p) => !p) }}
    >
      <div
        className={cn("flex h-screen overflow-hidden bg-background", className)}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  );
}

/* ─── Skeleton ─── */
function AppShellSkeleton() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar skeleton */}
      <div className="hidden lg:flex w-60 shrink-0 flex-col border-e border-sidebar-border bg-sidebar p-4 gap-3">
        {/* Logo */}
        <div className="flex items-center gap-2 px-1 py-1 mb-2">
          <div className="size-8 rounded-lg bg-muted/70 animate-pulse" />
          <div className="h-4 w-24 rounded bg-muted/50 animate-pulse" />
        </div>
        {/* Nav items */}
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-9 rounded-md bg-muted/40 animate-pulse"
            style={{ animationDelay: `${i * 60}ms` }}
          />
        ))}
        {/* Footer */}
        <div className="mt-auto border-t border-sidebar-border pt-3">
          <div className="flex items-center gap-2">
            <div className="size-8 rounded-full bg-muted/60 animate-pulse" />
            <div className="flex-1 space-y-1.5">
              <div className="h-3 w-20 rounded bg-muted/50 animate-pulse" />
              <div className="h-2.5 w-28 rounded bg-muted/40 animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      {/* Main area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="h-14 shrink-0 border-b border-border bg-background px-6 flex items-center gap-3">
          <div className="h-5 w-5 rounded bg-muted/60 animate-pulse lg:hidden" />
          <div className="h-4 w-48 rounded bg-muted/50 animate-pulse" />
          <div className="ms-auto flex gap-2">
            <div className="size-8 rounded bg-muted/40 animate-pulse" />
            <div className="size-8 rounded-full bg-muted/40 animate-pulse" />
          </div>
        </div>
        {/* Content */}
        <div className="flex-1 p-6 space-y-5 overflow-auto">
          <div className="h-8 w-56 rounded-lg bg-muted/50 animate-pulse" />
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-28 rounded-xl bg-muted/35 animate-pulse"
                style={{ animationDelay: `${i * 80}ms` }}
              />
            ))}
          </div>
          <div className="h-52 rounded-xl bg-muted/25 animate-pulse" />
        </div>
      </div>
    </div>
  );
}
