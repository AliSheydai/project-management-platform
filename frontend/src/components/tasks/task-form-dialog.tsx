"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { taskSchema, type TaskFormData } from "@/lib/validations";
import {
  TASK_STATUS_CONFIG,
  TASK_PRIORITY_CONFIG,
  KANBAN_COLUMNS,
} from "@/lib/constants";
import type { TaskPriority, TaskStatus } from "@/types";

interface TaskFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  loading?: boolean;
  defaultValues?: Partial<TaskFormData>;
  members?: { id: string; full_name: string }[];
  onSubmit: (data: TaskFormData) => Promise<void>;
}

export function TaskFormDialog({
  open,
  onOpenChange,
  title,
  loading,
  defaultValues,
  members = [],
  onSubmit,
}: TaskFormDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    values: {
      title: defaultValues?.title ?? "",
      description: defaultValues?.description ?? "",
      status: defaultValues?.status ?? "TODO",
      priority: defaultValues?.priority ?? "MEDIUM",
      assignee_id: defaultValues?.assignee_id ?? null,
      due_date: defaultValues?.due_date ?? null,
    },
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        onOpenChange(next);
        if (!next) reset();
      }}
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (data) => {
            await onSubmit(data);
            reset();
          })}
        >
          <div className="space-y-2">
            <Label htmlFor="task-title">عنوان</Label>
            <Input
              id="task-title"
              {...register("title")}
              aria-invalid={!!errors.title}
            />
            {errors.title && (
              <p className="text-xs text-destructive">{errors.title.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="task-description">توضیحات</Label>
            <Textarea id="task-description" rows={3} {...register("description")} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="task-status">وضعیت</Label>
              <select
                id="task-status"
                className={selectClass}
                {...register("status")}
              >
                {KANBAN_COLUMNS.map((s) => (
                  <option key={s} value={s}>
                    {TASK_STATUS_CONFIG[s as TaskStatus].label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-priority">اولویت</Label>
              <select
                id="task-priority"
                className={selectClass}
                {...register("priority")}
              >
                {(Object.keys(TASK_PRIORITY_CONFIG) as TaskPriority[]).map(
                  (p) => (
                    <option key={p} value={p}>
                      {TASK_PRIORITY_CONFIG[p].label}
                    </option>
                  )
                )}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="task-assignee">مسئول</Label>
              <select
                id="task-assignee"
                className={selectClass}
                {...register("assignee_id")}
              >
                <option value="">بدون مسئول</option>
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.full_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-due">سررسید</Label>
              <Input id="task-due" type="date" {...register("due_date")} />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              انصراف
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "در حال ذخیره..." : "ذخیره"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

const selectClass =
  "h-10 w-full border-0 border-b border-input bg-transparent text-sm outline-none focus-visible:border-ring";

export function useTaskFormDialogState() {
  const [open, setOpen] = useState(false);
  return { open, setOpen };
}
