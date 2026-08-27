"use client";

import { useState } from "react";
import { Loader2, Trash2 } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  ConfirmDialog,
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  TaskPriorityBadge,
  TaskStatusBadge,
  UserAvatar,
} from "@/components/shared";
import { useTask, useUpdateTask, useDeleteTask } from "@/features/tasks/hooks";
import {
  useTaskComments,
  useCreateComment,
  useDeleteComment,
  useTaskActivity,
} from "@/features/comments/hooks";
import { useProjectMembers } from "@/features/projects/hooks";
import { useAuth } from "@/hooks/use-auth";
import { formatRelativeDate, formatDate } from "@/lib/dates";
import {
  KANBAN_COLUMNS,
  TASK_PRIORITY_CONFIG,
  TASK_STATUS_CONFIG,
} from "@/lib/constants";
import type { TaskPriority, TaskStatus } from "@/types";
import { canEditTasks } from "@/lib/permissions";
import { useProject } from "@/features/projects/hooks";

interface TaskDetailSheetProps {
  projectId: string;
  taskId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskDetailSheet({
  projectId,
  taskId,
  open,
  onOpenChange,
}: TaskDetailSheetProps) {
  const { data: project } = useProject(projectId);
  const { data: task, isLoading, isError, refetch } = useTask(taskId);
  const { data: members } = useProjectMembers(projectId);
  const updateTask = useUpdateTask(projectId);
  const deleteTask = useDeleteTask(projectId);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const canEdit = canEditTasks(project?.current_user_role);

  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent
          side="left"
          className="w-full sm:max-w-lg overflow-y-auto"
        >
          <SheetHeader>
            <SheetTitle className="text-start">جزئیات تسک</SheetTitle>
          </SheetHeader>

          <div className="px-4 pb-6 space-y-6">
            {isLoading && <LoadingSkeleton count={5} />}
            {isError && <ErrorState retry={() => refetch()} />}
            {task && (
              <>
                <div className="space-y-3">
                  {canEdit ? (
                    <Input
                      className="text-base font-semibold"
                      defaultValue={task.title}
                      onBlur={(e) => {
                        if (e.target.value && e.target.value !== task.title) {
                          updateTask.mutate({
                            taskId: task.id,
                            data: { title: e.target.value },
                          });
                        }
                      }}
                    />
                  ) : (
                    <h2 className="text-base font-semibold">{task.title}</h2>
                  )}
                  <div className="flex flex-wrap gap-2">
                    <TaskStatusBadge status={task.status} />
                    <TaskPriorityBadge priority={task.priority} />
                  </div>
                </div>

                {canEdit && (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <Label>وضعیت</Label>
                      <select
                        className={selectClass}
                        value={task.status}
                        onChange={(e) =>
                          updateTask.mutate({
                            taskId: task.id,
                            data: { status: e.target.value },
                          })
                        }
                      >
                        {KANBAN_COLUMNS.map((s) => (
                          <option key={s} value={s}>
                            {TASK_STATUS_CONFIG[s as TaskStatus].label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <Label>اولویت</Label>
                      <select
                        className={selectClass}
                        value={task.priority}
                        onChange={(e) =>
                          updateTask.mutate({
                            taskId: task.id,
                            data: { priority: e.target.value },
                          })
                        }
                      >
                        {(
                          Object.keys(TASK_PRIORITY_CONFIG) as TaskPriority[]
                        ).map((p) => (
                          <option key={p} value={p}>
                            {TASK_PRIORITY_CONFIG[p].label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <Label>مسئول</Label>
                      <select
                        className={selectClass}
                        value={task.assignee_id ?? ""}
                        onChange={(e) => {
                          const value = e.target.value;
                          updateTask.mutate({
                            taskId: task.id,
                            data: value
                              ? { assignee_id: value }
                              : { unassign: true },
                          });
                        }}
                      >
                        <option value="">بدون مسئول</option>
                        {members?.map((m) => (
                          <option key={m.user_id} value={m.user_id}>
                            {m.user.full_name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-1.5">
                      <Label>سررسید</Label>
                      <Input
                        type="date"
                        defaultValue={
                          task.due_date ? task.due_date.slice(0, 10) : ""
                        }
                        onBlur={(e) => {
                          const value = e.target.value;
                          updateTask.mutate({
                            taskId: task.id,
                            data: value
                              ? { due_date: value }
                              : { clear_due_date: true },
                          });
                        }}
                      />
                    </div>
                  </div>
                )}

                <div className="space-y-1.5">
                  <Label>توضیحات</Label>
                  {canEdit ? (
                    <Textarea
                      rows={4}
                      defaultValue={task.description ?? ""}
                      onBlur={(e) => {
                        if (e.target.value !== (task.description ?? "")) {
                          updateTask.mutate({
                            taskId: task.id,
                            data: { description: e.target.value },
                          });
                        }
                      }}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {task.description || "بدون توضیحات"}
                    </p>
                  )}
                </div>

                {!canEdit && task.due_date && (
                  <p className="text-sm text-muted-foreground">
                    سررسید: {formatDate(task.due_date)}
                  </p>
                )}

                <CommentsSection taskId={task.id} canEdit={canEdit} />
                <ActivitySection taskId={task.id} />

                {canEdit && (
                  <Button
                    variant="destructive"
                    className="w-full"
                    onClick={() => setConfirmDelete(true)}
                  >
                    <Trash2 className="size-4" />
                    حذف تسک
                  </Button>
                )}
              </>
            )}
          </div>
        </SheetContent>
      </Sheet>

      <ConfirmDialog
        open={confirmDelete}
        onOpenChange={setConfirmDelete}
        title="حذف تسک"
        description="این تسک برای همیشه حذف می‌شود."
        confirmLabel="حذف"
        variant="destructive"
        loading={deleteTask.isPending}
        onConfirm={async () => {
          if (!taskId) return;
          await deleteTask.mutateAsync(taskId);
          setConfirmDelete(false);
          onOpenChange(false);
        }}
      />
    </>
  );
}

function CommentsSection({
  taskId,
  canEdit,
}: {
  taskId: string;
  canEdit: boolean;
}) {
  const { user } = useAuth();
  const { data, isLoading } = useTaskComments(taskId);
  const createComment = useCreateComment(taskId);
  const deleteComment = useDeleteComment(taskId);
  const [content, setContent] = useState("");

  return (
    <section className="space-y-3 border-t border-border pt-4">
      <h3 className="text-sm font-semibold">نظرات</h3>
      {isLoading && <LoadingSkeleton count={2} />}
      {!isLoading && !data?.items.length && (
        <EmptyState title="نظری ثبت نشده" className="py-6" />
      )}
      <ul className="space-y-3">
        {data?.items.map((c) => (
          <li key={c.id} className="flex gap-2">
            <UserAvatar
              name={c.author.full_name}
              avatarUrl={c.author.avatar_url}
              size="sm"
            />
            <div className="min-w-0 flex-1 rounded-md bg-muted/40 px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium">{c.author.full_name}</p>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-muted-foreground">
                    {formatRelativeDate(c.created_at)}
                  </span>
                  {(canEdit || user?.id === c.author_id) && (
                    <button
                      type="button"
                      className="text-[10px] text-destructive"
                      onClick={() => deleteComment.mutate(c.id)}
                    >
                      حذف
                    </button>
                  )}
                </div>
              </div>
              <p className="mt-1 text-sm whitespace-pre-wrap">{c.content}</p>
            </div>
          </li>
        ))}
      </ul>
      {canEdit && (
        <form
          className="space-y-2"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!content.trim()) return;
            await createComment.mutateAsync(content.trim());
            setContent("");
          }}
        >
          <Textarea
            rows={2}
            placeholder="نظر خود را بنویسید..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <Button
            type="submit"
            size="sm"
            disabled={createComment.isPending || !content.trim()}
          >
            {createComment.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              "ارسال نظر"
            )}
          </Button>
        </form>
      )}
    </section>
  );
}

function ActivitySection({ taskId }: { taskId: string }) {
  const { data, isLoading } = useTaskActivity(taskId);
  return (
    <section className="space-y-3 border-t border-border pt-4">
      <h3 className="text-sm font-semibold">فعالیت</h3>
      {isLoading && <LoadingSkeleton count={2} />}
      <ul className="space-y-2">
        {data?.items.map((a) => (
          <li key={a.id} className="flex gap-2 text-sm">
            <UserAvatar
              name={a.user.full_name}
              avatarUrl={a.user.avatar_url}
              size="sm"
            />
            <div>
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
    </section>
  );
}

const selectClass =
  "h-10 w-full border-0 border-b border-input bg-transparent text-sm outline-none focus-visible:border-ring";
