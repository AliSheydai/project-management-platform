"use client";

import { PageContainer } from "@/components/layout/page-container";
import {
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  UserAvatar,
} from "@/components/shared";
import { useProjectActivity } from "@/features/comments/hooks";
import { formatRelativeDate } from "@/lib/dates";

export function ActivityView({ projectId }: { projectId: string }) {
  const { data, isLoading, isError, refetch } = useProjectActivity(projectId);

  return (
    <PageContainer>
      <div className="mb-6">
        <h2 className="text-base font-semibold">فعالیت‌های پروژه</h2>
        <p className="text-sm text-muted-foreground">
          تاریخچه تغییرات و رویدادهای پروژه
        </p>
      </div>

      {isLoading && <LoadingSkeleton count={6} />}
      {isError && <ErrorState retry={() => refetch()} />}

      {!isLoading && !isError && data && data.items.length === 0 && (
        <EmptyState title="هنوز فعالیتی ثبت نشده" />
      )}

      {!isLoading && !isError && data && data.items.length > 0 && (
        <ol className="relative space-y-0 border-s border-border ms-3">
          {data.items.map((item) => (
            <li key={item.id} className="relative pb-6 ps-6 last:pb-0">
              <span className="absolute start-[-5px] top-1.5 size-2.5 rounded-full bg-primary" />
              <div className="flex gap-3">
                <UserAvatar
                  name={item.user.full_name}
                  avatarUrl={item.user.avatar_url}
                  size="sm"
                />
                <div className="min-w-0">
                  <p className="text-sm">
                    <span className="font-medium">{item.user.full_name}</span>{" "}
                    <span className="text-muted-foreground">{item.action}</span>
                    {item.entity_type && (
                      <span className="text-muted-foreground">
                        {" "}
                        · {item.entity_type}
                      </span>
                    )}
                  </p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {formatRelativeDate(item.created_at)}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </PageContainer>
  );
}
