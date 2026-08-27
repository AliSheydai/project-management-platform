"use client";

import { useMemo } from "react";
import Link from "next/link";
import {
  FolderKanban,
  ListTodo,
  Bell,
  Activity,
  ArrowLeft,
} from "lucide-react";
import { PageContainer, PageHeader } from "@/components/layout/page-container";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState, CardSkeleton } from "@/components/shared";
import { TaskStatusBadge, TaskPriorityBadge } from "@/components/shared";
import { useProjects } from "@/features/projects/hooks";
import { useSearchTasks } from "@/features/tasks/hooks";
import { useNotifications } from "@/features/notifications/hooks";
import { formatRelativeDate } from "@/lib/dates";
import { useAuth } from "@/hooks/use-auth";

export function DashboardView() {
  const { user } = useAuth();
  const projectsQuery = useProjects({ page_size: 6, is_archived: false });
  const tasksQuery = useSearchTasks({
    page_size: 8,
    sort_by: "updated_at",
    order: "desc",
  });
  const notificationsQuery = useNotifications({ page_size: 5 });

  const stats = useMemo(() => {
    const projects = projectsQuery.data;
    const tasks = tasksQuery.data;
    const statusCounts = tasks?.facets?.status_counts ?? {};
    const done = statusCounts.DONE ?? 0;
    const inProgress = statusCounts.IN_PROGRESS ?? 0;
    return {
      projects: projects?.total ?? 0,
      tasks: tasks?.total ?? 0,
      done,
      inProgress,
      unread: notificationsQuery.data?.unread_count ?? 0,
    };
  }, [projectsQuery.data, tasksQuery.data, notificationsQuery.data]);

  const isLoading =
    projectsQuery.isLoading ||
    tasksQuery.isLoading ||
    notificationsQuery.isLoading;
  const isError =
    projectsQuery.isError || tasksQuery.isError || notificationsQuery.isError;

  return (
    <PageContainer>
      <PageHeader
        title={`سلام، ${user?.first_name ?? "کاربر"}`}
        description="خلاصه وضعیت پروژه‌ها و تسک‌های شما"
      >
        <Button nativeButton={false} render={<Link href="/projects" />}>
          پروژه‌ها
          <ArrowLeft className="size-4" />
        </Button>
      </PageHeader>

      {isError && (
        <ErrorState
          retry={() => {
            projectsQuery.refetch();
            tasksQuery.refetch();
            notificationsQuery.refetch();
          }}
        />
      )}

      {!isError && (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 mb-8">
            <StatCard
              label="پروژه‌ها"
              value={stats.projects}
              icon={<FolderKanban className="size-4" />}
              loading={isLoading}
            />
            <StatCard
              label="تسک‌ها"
              value={stats.tasks}
              icon={<ListTodo className="size-4" />}
              loading={isLoading}
            />
            <StatCard
              label="در حال انجام"
              value={stats.inProgress}
              icon={<Activity className="size-4" />}
              loading={isLoading}
            />
            <StatCard
              label="اعلان خوانده‌نشده"
              value={stats.unread}
              icon={<Bell className="size-4" />}
              loading={isLoading}
            />
          </div>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader className="flex-row items-center justify-between border-b">
                <CardTitle className="normal-case tracking-normal text-base">
                  تسک‌های اخیر
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  nativeButton={false}
                  render={<Link href="/projects" />}
                >
                  مشاهده همه
                </Button>
              </CardHeader>
              <CardContent className="pt-4">
                {tasksQuery.isLoading ? (
                  <CardSkeleton />
                ) : !tasksQuery.data?.items.length ? (
                  <EmptyState
                    title="هنوز تسکی ندارید"
                    description="با ایجاد پروژه و تسک شروع کنید"
                    action={{
                      label: "رفتن به پروژه‌ها",
                      onClick: () => {
                        window.location.href = "/projects";
                      },
                    }}
                  />
                ) : (
                  <ul className="divide-y divide-border">
                    {tasksQuery.data.items.map((task) => (
                      <li key={task.id}>
                        <Link
                          href={`/projects/${task.project_id}/tasks?task=${task.id}`}
                          className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between hover:bg-muted/40 -mx-2 px-2 rounded-md transition-colors"
                        >
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">
                              {task.title}
                            </p>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {formatRelativeDate(task.updated_at)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <TaskStatusBadge status={task.status} />
                            <TaskPriorityBadge priority={task.priority} />
                          </div>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card>
                <CardHeader className="border-b">
                  <CardTitle className="normal-case tracking-normal text-base">
                    پروژه‌های فعال
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4">
                  {projectsQuery.isLoading ? (
                    <CardSkeleton />
                  ) : !projectsQuery.data?.items.length ? (
                    <EmptyState
                      title="پروژه‌ای نیست"
                      description="اولین پروژه را بسازید"
                    />
                  ) : (
                    <ul className="space-y-2">
                      {projectsQuery.data.items.map((project) => (
                        <li key={project.id}>
                          <Link
                            href={`/projects/${project.id}/overview`}
                            className="flex items-center justify-between rounded-md px-2 py-2 hover:bg-muted/40 transition-colors"
                          >
                            <div className="min-w-0">
                              <p className="text-sm font-medium truncate">
                                {project.name}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {project.members_count} عضو
                              </p>
                            </div>
                            <ArrowLeft className="size-4 text-muted-foreground shrink-0" />
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex-row items-center justify-between border-b">
                  <CardTitle className="normal-case tracking-normal text-base">
                    اعلان‌ها
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    nativeButton={false}
                    render={<Link href="/notifications" />}
                  >
                    همه
                  </Button>
                </CardHeader>
                <CardContent className="pt-4">
                  {notificationsQuery.isLoading ? (
                    <CardSkeleton />
                  ) : !notificationsQuery.data?.items.length ? (
                    <EmptyState title="اعلانی نیست" />
                  ) : (
                    <ul className="space-y-3">
                      {notificationsQuery.data.items.map((n) => (
                        <li key={n.id} className="text-sm">
                          <p
                            className={
                              n.is_read
                                ? "text-muted-foreground"
                                : "font-medium text-foreground"
                            }
                          >
                            {n.title}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {formatRelativeDate(n.created_at)}
                          </p>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </>
      )}
    </PageContainer>
  );
}

function StatCard({
  label,
  value,
  icon,
  loading,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  loading?: boolean;
}) {
  return (
    <Card size="sm" className="py-4">
      <CardContent className="flex items-center gap-3 px-4">
        <div className="flex size-9 items-center justify-center rounded-md bg-muted text-muted-foreground">
          {icon}
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-xl font-semibold tabular-nums">
            {loading ? "—" : value.toLocaleString("fa-IR")}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
