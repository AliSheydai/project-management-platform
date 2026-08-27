"use client";

import { useMemo, useState } from "react";
import type { Task, TaskStatus } from "@/types";
import { KANBAN_COLUMNS, TASK_STATUS_CONFIG } from "@/lib/constants";
import { TaskPriorityBadge, UserAvatar } from "@/components/shared";
import { useReorderTask } from "@/features/tasks/hooks";
import { cn } from "@/lib/utils";

interface KanbanBoardProps {
  projectId: string;
  tasks: Task[];
  onTaskClick: (taskId: string) => void;
  canEdit: boolean;
}

export function KanbanBoard({
  projectId,
  tasks,
  onTaskClick,
  canEdit,
}: KanbanBoardProps) {
  const reorder = useReorderTask(projectId);
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [overStatus, setOverStatus] = useState<TaskStatus | null>(null);

  const columns = useMemo(() => {
    const map = Object.fromEntries(
      KANBAN_COLUMNS.map((s) => [s, [] as Task[]])
    ) as Record<TaskStatus, Task[]>;
    for (const task of tasks) {
      map[task.status]?.push(task);
    }
    for (const status of KANBAN_COLUMNS) {
      map[status].sort((a, b) => a.position - b.position);
    }
    return map;
  }, [tasks]);

  const handleDrop = (status: TaskStatus) => {
    if (!draggingId || !canEdit) return;
    const column = columns[status];
    const position = column.length;
    reorder.mutate({ taskId: draggingId, status, position });
    setDraggingId(null);
    setOverStatus(null);
  };

  return (
    <div className="flex gap-3 overflow-x-auto pb-4 min-h-[420px]">
      {KANBAN_COLUMNS.map((status) => (
        <div
          key={status}
          className={cn(
            "flex w-72 shrink-0 flex-col rounded-lg border border-border bg-muted/30",
            overStatus === status && "ring-2 ring-primary/40"
          )}
          onDragOver={(e) => {
            if (!canEdit) return;
            e.preventDefault();
            setOverStatus(status);
          }}
          onDragLeave={() => setOverStatus((s) => (s === status ? null : s))}
          onDrop={(e) => {
            e.preventDefault();
            handleDrop(status);
          }}
        >
          <div className="flex items-center justify-between border-b border-border px-3 py-2.5">
            <h3 className="text-sm font-medium">
              {TASK_STATUS_CONFIG[status].label}
            </h3>
            <span className="text-xs tabular-nums text-muted-foreground">
              {columns[status].length.toLocaleString("fa-IR")}
            </span>
          </div>
          <div className="flex flex-1 flex-col gap-2 p-2">
            {columns[status].map((task) => (
              <button
                key={task.id}
                type="button"
                draggable={canEdit}
                onDragStart={() => setDraggingId(task.id)}
                onDragEnd={() => {
                  setDraggingId(null);
                  setOverStatus(null);
                }}
                onClick={() => onTaskClick(task.id)}
                className={cn(
                  "rounded-md border border-border bg-card p-3 text-start shadow-sm transition-all hover:border-foreground/20",
                  draggingId === task.id && "opacity-50"
                )}
              >
                <p className="text-sm font-medium line-clamp-2">{task.title}</p>
                <div className="mt-2 flex items-center justify-between gap-2">
                  <TaskPriorityBadge priority={task.priority} />
                  {task.assignee && (
                    <UserAvatar
                      name={task.assignee.full_name}
                      avatarUrl={task.assignee.avatar_url}
                      size="sm"
                    />
                  )}
                </div>
              </button>
            ))}
            {!columns[status].length && (
              <div className="rounded-md border border-dashed border-border p-4 text-center text-xs text-muted-foreground">
                خالی
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
