"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api/tasks";
import { searchApi } from "@/lib/api/search";
import { queryKeys } from "@/lib/query-keys";
import { getApiErrorMessage } from "@/lib/api/error";
import { toastUtils } from "@/lib/utils/toast";
import type { Task } from "@/types";

export function useProjectTasks(
  projectId: string,
  params?: {
    status?: string;
    priority?: string;
    assignee_id?: string;
    unassigned?: boolean;
    q?: string;
    sort_by?: string;
    order?: "asc" | "desc";
    page?: number;
    page_size?: number;
  }
) {
  return useQuery({
    queryKey: queryKeys.projectTasks(projectId, params),
    queryFn: async () => {
      const { data } = await tasksApi.list(projectId, params);
      return data;
    },
    enabled: !!projectId,
  });
}

export function useTask(taskId: string | null) {
  return useQuery({
    queryKey: queryKeys.task(taskId ?? ""),
    queryFn: async () => {
      const { data } = await tasksApi.getById(taskId!);
      return data;
    },
    enabled: !!taskId,
  });
}

export function useSearchTasks(params?: {
  q?: string;
  project_id?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  order?: "asc" | "desc";
}) {
  return useQuery({
    queryKey: queryKeys.searchTasks(params),
    queryFn: async () => {
      const { data } = await searchApi.searchTasks(params);
      return data;
    },
  });
}

export function useCreateTask(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      title: string;
      description?: string;
      status?: string;
      priority?: string;
      assignee_id?: string;
      due_date?: string;
    }) => tasksApi.create(projectId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["project-tasks", projectId] });
      qc.invalidateQueries({ queryKey: ["search-tasks"] });
      toastUtils.success("تسک ایجاد شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useUpdateTask(projectId?: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      taskId,
      data,
    }: {
      taskId: string;
      data: Parameters<typeof tasksApi.update>[1];
    }) => tasksApi.update(taskId, data).then((r) => r.data),
    onSuccess: (task) => {
      if (projectId) {
        qc.invalidateQueries({ queryKey: ["project-tasks", projectId] });
      } else {
        qc.invalidateQueries({ queryKey: ["project-tasks"] });
      }
      qc.invalidateQueries({ queryKey: queryKeys.task(task.id) });
      qc.invalidateQueries({ queryKey: ["search-tasks"] });
      toastUtils.success("تسک به‌روزرسانی شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useReorderTask(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      taskId,
      position,
      status,
    }: {
      taskId: string;
      position: number;
      status?: string;
    }) => tasksApi.reorder(taskId, { position, status }).then((r) => r.data),
    onMutate: async ({ taskId, status, position }) => {
      await qc.cancelQueries({ queryKey: ["project-tasks", projectId] });
      const previous = qc.getQueriesData<{ items: Task[] }>({
        queryKey: ["project-tasks", projectId],
      });
      qc.setQueriesData<{ items: Task[]; total: number; page: number; page_size: number; pages: number }>(
        { queryKey: ["project-tasks", projectId] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((t) =>
              t.id === taskId
                ? {
                    ...t,
                    position,
                    ...(status ? { status: status as Task["status"] } : {}),
                  }
                : t
            ),
          };
        }
      );
      return { previous };
    },
    onError: (e, _v, ctx) => {
      ctx?.previous?.forEach(([key, data]) => {
        qc.setQueryData(key, data);
      });
      toastUtils.error("خطا در جابجایی", getApiErrorMessage(e));
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["project-tasks", projectId] });
    },
  });
}

export function useDeleteTask(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => tasksApi.delete(taskId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["project-tasks", projectId] });
      qc.invalidateQueries({ queryKey: ["search-tasks"] });
      toastUtils.success("تسک حذف شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}
