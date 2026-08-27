"use client";

import Link from "next/link";
import {
  ListTodo,
  Users,
  Archive,
  RotateCcw,
} from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RoleBadge, UserAvatar, ProgressBar } from "@/components/shared";
import { useProject, useUpdateProject } from "@/features/projects/hooks";
import { useProjectTasks } from "@/features/tasks/hooks";
import { useProjectActivity } from "@/features/comments/hooks";
import { formatRelativeDate } from "@/lib/dates";
import { KANBAN_COLUMNS, TASK_STATUS_CONFIG } from "@/lib/constants";
import { canManageProject } from "@/lib/permissions";

export function ProjectOverviewView({ projectId }: { projectId: string }) {
  const { data: project } = useProject(projectId);
  const { data: tasks } = useProjectTasks(projectId, { page_size: 100 });
  const { data: activity } = useProjectActivity(projectId);
  const updateMutation = useUpdateProject(projectId);

  if (!project) return null;

  const items = tasks?.items ?? [];
  const total = items.length || 1;
  const done = items.filter((t) => t.status === "DONE").length;
  const progress = Math.round((done / total) * 100);
  const statusBreakdown = KANBAN_COLUMNS.map((status) => ({
    status,
    count: items.filter((t) => t.status === status).length,
    label: TASK_STATUS_CONFIG[status].label,
  }));

  const canManage = canManageProject(project.current_user_role);

  return (
    <PageContainer>
      <div className="mb-6 flex flex-wrap items-center gap-2">
        {canManage && (
          <Button
            variant="outline"
            size="sm"
            disabled={updateMutation.isPending}
            onClick={() =>
              updateMutation.mutate({ is_archived: !project.is_archived })
            }
          >
            {project.is_archived ? (
              <>
                <RotateCcw className="size-4" />
                بازگردانی از بایگانی
              </>
            ) : (
              <>
                <Archive className="size-4" />
                بایگانی پروژه
              </>
            )}
          </Button>
        )}
        <Button
          size="sm"
          nativeButton={false}
          render={<Link href={`/projects/${projectId}/tasks`} />}
        >
          <ListTodo className="size-4" />
          تسک‌ها
        </Button>
        <Button
          variant="outline"
          size="sm"
          nativeButton={false}
          render={<Link href={`/projects/${projectId}/members`} />}
        >
          <Users className="size-4" />
          اعضا
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="border-b">
            <CardTitle className="normal-case tracking-normal text-base">
              پیشرفت
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5 pt-5">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">انجام‌شده</span>
                <span className="font-medium tabular-nums">
                  {done.toLocaleString("fa-IR")} /{" "}
                  {items.length.toLocaleString("fa-IR")} ({progress}٪)
                </span>
              </div>
              <ProgressBar value={progress} />
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              {statusBreakdown.map((s) => (
                <div
                  key={s.status}
                  className="rounded-md bg-muted/50 px-3 py-2 text-center"
                >
                  <p className="text-lg font-semibold tabular-nums">
                    {s.count.toLocaleString("fa-IR")}
                  </p>
                  <p className="text-[11px] text-muted-foreground">{s.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="border-b">
            <CardTitle className="normal-case tracking-normal text-base">
              تیم
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 pt-4">
            {project.members.slice(0, 6).map((m) => (
              <div key={m.id} className="flex items-center gap-3">
                <UserAvatar
                  name={m.user.full_name}
                  avatarUrl={m.user.avatar_url}
                  size="sm"
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">
                    {m.user.full_name}
                  </p>
                  <p className="truncate text-xs text-muted-foreground">
                    {m.user.email}
                  </p>
                </div>
                <RoleBadge role={m.role} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader className="border-b">
            <CardTitle className="normal-case tracking-normal text-base">
              فعالیت‌های اخیر
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            {!activity?.items.length ? (
              <p className="text-sm text-muted-foreground">هنوز فعالیتی ثبت نشده</p>
            ) : (
              <ul className="space-y-3">
                {activity.items.slice(0, 8).map((a) => (
                  <li key={a.id} className="flex gap-3 text-sm">
                    <UserAvatar
                      name={a.user.full_name}
                      avatarUrl={a.user.avatar_url}
                      size="sm"
                    />
                    <div className="min-w-0">
                      <p>
                        <span className="font-medium">{a.user.full_name}</span>{" "}
                        <span className="text-muted-foreground">{a.action}</span>
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeDate(a.created_at)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
