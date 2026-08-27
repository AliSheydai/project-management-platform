"use client";

import Link from "next/link";
import { Bell } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api/notifications";
import { useAuthStore } from "@/lib/auth/session";
import { cn } from "@/lib/utils";

export function NotificationBell({ className }: { className?: string }) {
  const { isAuthenticated } = useAuthStore();

  const { data } = useQuery({
    queryKey: ["notifications-unread-count"],
    queryFn: () => notificationsApi.getUnreadCount().then((r) => r.data),
    enabled: isAuthenticated,
    refetchInterval: 30_000, // poll every 30s
    staleTime: 15_000,
  });

  const count = data?.unread_count ?? 0;
  const displayCount = count > 99 ? "99+" : count > 0 ? String(count) : null;

  return (
    <Link
      href="/notifications"
      aria-label={`اعلان‌ها${count > 0 ? ` — ${count} خوانده نشده` : ""}`}
      className={cn(
        "relative inline-flex size-9 items-center justify-center rounded-md",
        "text-muted-foreground hover:bg-muted hover:text-foreground",
        "transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-ring",
        className
      )}
    >
      <Bell className="size-4" />
      {displayCount && (
        <span
          className={cn(
            "absolute top-1 end-1 flex items-center justify-center",
            "min-w-[16px] h-4 px-1 rounded-full",
            "bg-primary text-primary-foreground text-[10px] font-semibold leading-none",
            "animate-fade-in"
          )}
        >
          {displayCount}
        </span>
      )}
    </Link>
  );
}
