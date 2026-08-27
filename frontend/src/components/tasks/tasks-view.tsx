"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { LayoutGrid, List, Plus } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  Pagination,
  SearchInput,
  TableSkeleton,
  TaskPriorityBadge,
  TaskStatusBadge,
  UserAvatar,
} from "@/components/shared";
import {
  useCreateTask,
  useProjectTasks,
} from "@/features/tasks/hooks";
import { useProject, useProjectMembers } from "@/features/projects/hooks";
import { canEditTasks } from "@/lib/permissions";
import { formatDate, isOverdue } from "@/lib/dates";
import {
  KANBAN_COLUMNS,
  TASK_PRIORITY_CONFIG,
  TASK_STATUS_CONFIG,
} from "@/lib/constants";
import type { TaskPriority, TaskStatus } from "@/types";
import { TaskFormDialog } from "./task-form-dialog";
import { KanbanBoard } from "./kanban-board";
import { TaskDetailSheet } from "./task-detail-sheet";
import { cn } from "@/lib/utils";

export function TasksView({ projectId }: { projectId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [view, setView] = useState<"list" | "kanban">("kanban");
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("");
  const [priority, setPriority] = useState<string>("");
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(
    searchParams.get("task")
  );

  useEffect(() => {
    const fromUrl = searchParams.get("task");
    if (fromUrl) setSelectedTaskId(fromUrl);
  }, [searchParams]);

  const { data: project } = useProject(projectId);
  const { data: members } = useProjectMembers(projectId);
  const canEdit = canEditTasks(project?.current_user_role);

  const listParams = useMemo(
    () => ({
      q: q || undefined,
      status: status || undefined,
      priority: priority || undefined,
      page: view === "list" ? page : 1,
      page_size: view === "list" ? 20 : 100,
      sort_by: "position",
      order: "asc" as const,
    }),
    [q, status, priority, page, view]
  );

  const { data, isLoading, isError, refetch } = useProjectTasks(
    projectId,
    listParams
  );
  const createTask = useCreateTask(projectId);

  const openTask = (taskId: string) => {
    setSelectedTaskId(taskId);
    const params = new URLSearchParams(searchParams.toString());
    params.set("task", taskId);
    router.replace(`?${params.toString()}`, { scroll: false });
  };

  const closeTask = (open: boolean) => {
    if (!open) {
      setSelectedTaskId(null);
      const params = new URLSearchParams(searchParams.toString());
      params.delete("task");
      const qs = params.toString();
      router.replace(qs ? `?${qs}` : "?", { scroll: false });
    }
  };

  return (
    <PageContainer>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-1 rounded-md border border-border p-1 w-fit">
          <Button
            size="sm"
            variant={view === "kanban" ? "secondary" : "ghost"}
            onClick={() => setView("kanban")}
          >
            <LayoutGrid className="size-4" />
            کانبان
          </Button>
          <Button
            size="sm"
            variant={view === "list" ? "secondary" : "ghost"}
            onClick={() => setView("list")}
          >
            <List className="size-4" />
            لیست
          </Button>
        </div>
        {canEdit && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="size-4" />
            تسک جدید
          </Button>
        )}
      </div>

      <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center">
        <SearchInput
          className="lg:max-w-xs"
          placeholder="جستجوی تسک..."
          onChange={(value) => {
            setQ(value);
            setPage(1);
          }}
        />
        <select
          className={selectClass}
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
          aria-label="فیلتر وضعیت"
        >
          <option value="">همه وضعیت‌ها</option>
          {KANBAN_COLUMNS.map((s) => (
            <option key={s} value={s}>
              {TASK_STATUS_CONFIG[s as TaskStatus].label}
            </option>
          ))}
        </select>
        <select
          className={selectClass}
          value={priority}
          onChange={(e) => {
            setPriority(e.target.value);
            setPage(1);
          }}
          aria-label="فیلتر اولویت"
        >
          <option value="">همه اولویت‌ها</option>
          {(Object.keys(TASK_PRIORITY_CONFIG) as TaskPriority[]).map((p) => (
            <option key={p} value={p}>
              {TASK_PRIORITY_CONFIG[p].label}
            </option>
          ))}
        </select>
      </div>

      {isError && <ErrorState retry={() => refetch()} />}
      {isLoading && <TableSkeleton rows={6} columns={4} />}

      {!isLoading && !isError && data && data.items.length === 0 && (
        <EmptyState
          title="تسکی یافت نشد"
          description="یک تسک جدید بسازید یا فیلترها را تغییر دهید"
          action={
            canEdit
              ? { label: "ایجاد تسک", onClick: () => setCreateOpen(true) }
              : undefined
          }
        />
      )}

      {!isLoading && !isError && data && data.items.length > 0 && (
        <>
          {view === "kanban" ? (
            <KanbanBoard
              projectId={projectId}
              tasks={data.items}
              onTaskClick={openTask}
              canEdit={canEdit}
            />
          ) : (
            <>
              <div className="overflow-x-auto rounded-lg border border-border">
                <table className="w-full min-w-[640px] text-sm">
                  <thead className="bg-muted/40 text-muted-foreground">
                    <tr className="text-start">
                      <th className="px-3 py-2.5 font-medium">عنوان</th>
                      <th className="px-3 py-2.5 font-medium">وضعیت</th>
                      <th className="px-3 py-2.5 font-medium">اولویت</th>
                      <th className="px-3 py-2.5 font-medium">مسئول</th>
                      <th className="px-3 py-2.5 font-medium">سررسید</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((task) => (
                      <tr
                        key={task.id}
                        className="border-t border-border cursor-pointer hover:bg-muted/30"
                        onClick={() => openTask(task.id)}
                      >
                        <td className="px-3 py-3 font-medium">{task.title}</td>
                        <td className="px-3 py-3">
                          <TaskStatusBadge status={task.status} />
                        </td>
                        <td className="px-3 py-3">
                          <TaskPriorityBadge priority={task.priority} />
                        </td>
                        <td className="px-3 py-3">
                          {task.assignee ? (
                            <span className="inline-flex items-center gap-2">
                              <UserAvatar
                                name={task.assignee.full_name}
                                avatarUrl={task.assignee.avatar_url}
                                size="sm"
                              />
                              {task.assignee.full_name}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </td>
                        <td
                          className={cn(
                            "px-3 py-3",
                            isOverdue(task.due_date) && "text-destructive"
                          )}
                        >
                          {task.due_date ? formatDate(task.due_date) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                className="mt-6"
                page={data.page}
                pages={data.pages}
                onPageChange={setPage}
              />
            </>
          )}
        </>
      )}

      <TaskFormDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        title="تسک جدید"
        loading={createTask.isPending}
        members={
          members?.map((m) => ({
            id: m.user_id,
            full_name: m.user.full_name,
          })) ?? []
        }
        onSubmit={async (values) => {
          await createTask.mutateAsync({
            title: values.title,
            description: values.description,
            status: values.status,
            priority: values.priority,
            assignee_id: values.assignee_id || undefined,
            due_date: values.due_date || undefined,
          });
          setCreateOpen(false);
        }}
      />

      <TaskDetailSheet
        projectId={projectId}
        taskId={selectedTaskId}
        open={!!selectedTaskId}
        onOpenChange={closeTask}
      />
    </PageContainer>
  );
}

const selectClass =
  "h-10 min-w-[140px] border-0 border-b border-input bg-transparent text-sm outline-none focus-visible:border-ring";
