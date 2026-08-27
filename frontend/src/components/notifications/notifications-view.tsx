"use client";

import { useRouter } from "next/navigation";
import { CheckCheck, Trash2 } from "lucide-react";
import { PageContainer, PageHeader } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  Pagination,
  UserAvatar,
} from "@/components/shared";
import {
  useDeleteNotification,
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "@/features/notifications/hooks";
import { formatRelativeDate } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { useState } from "react";

export function NotificationsView() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, refetch } = useNotifications({
    page,
    page_size: 20,
  });
  const markRead = useMarkNotificationRead();
  const markAll = useMarkAllNotificationsRead();
  const remove = useDeleteNotification();

  const handleOpen = async (id: string, isRead: boolean, payload: Record<string, unknown> | null) => {
    if (!isRead) {
      await markRead.mutateAsync(id);
    }
    const projectId = payload?.project_id as string | undefined;
    const taskId = payload?.task_id as string | undefined;
    if (projectId && taskId) {
      router.push(`/projects/${projectId}/tasks?task=${taskId}`);
    } else if (projectId) {
      router.push(`/projects/${projectId}/overview`);
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="اعلان‌ها"
        description={
          data
            ? `${data.unread_count.toLocaleString("fa-IR")} خوانده‌نشده`
            : "مرکز اعلان‌های شما"
        }
      >
        <Button
          variant="outline"
          size="sm"
          disabled={markAll.isPending || !data?.unread_count}
          onClick={() => markAll.mutate()}
        >
          <CheckCheck className="size-4" />
          خواندن همه
        </Button>
      </PageHeader>

      {isLoading && <LoadingSkeleton count={5} />}
      {isError && <ErrorState retry={() => refetch()} />}

      {!isLoading && !isError && data && data.items.length === 0 && (
        <EmptyState
          title="اعلانی ندارید"
          description="وقتی رویدادی رخ دهد اینجا نمایش داده می‌شود"
        />
      )}

      {!isLoading && !isError && data && data.items.length > 0 && (
        <>
          <ul className="divide-y divide-border rounded-lg border border-border">
            {data.items.map((n) => (
              <li
                key={n.id}
                className={cn(
                  "flex items-start gap-3 p-4 transition-colors",
                  !n.is_read && "bg-primary/5"
                )}
              >
                {n.actor ? (
                  <UserAvatar
                    name={n.actor.full_name}
                    avatarUrl={n.actor.avatar_url}
                    size="sm"
                  />
                ) : (
                  <div className="size-6 rounded-full bg-muted" />
                )}
                <button
                  type="button"
                  className="min-w-0 flex-1 text-start"
                  onClick={() => handleOpen(n.id, n.is_read, n.payload)}
                >
                  <p
                    className={cn(
                      "text-sm",
                      !n.is_read ? "font-semibold" : "font-medium"
                    )}
                  >
                    {n.title}
                  </p>
                  <p className="mt-0.5 text-sm text-muted-foreground line-clamp-2">
                    {n.message}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatRelativeDate(n.created_at)}
                  </p>
                </button>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  aria-label="حذف اعلان"
                  onClick={() => remove.mutate(n.id)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </li>
            ))}
          </ul>
          <Pagination
            className="mt-6"
            page={data.page}
            pages={data.pages}
            onPageChange={setPage}
          />
        </>
      )}
    </PageContainer>
  );
}
