"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { commentsApi } from "@/lib/api/comments";
import { activityApi } from "@/lib/api/activity";
import { queryKeys } from "@/lib/query-keys";
import { getApiErrorMessage } from "@/lib/api/error";
import { toastUtils } from "@/lib/utils/toast";

export function useTaskComments(taskId: string | null) {
  return useQuery({
    queryKey: queryKeys.taskComments(taskId ?? ""),
    queryFn: async () => {
      const { data } = await commentsApi.list(taskId!, { page_size: 50 });
      return data;
    },
    enabled: !!taskId,
  });
}

export function useCreateComment(taskId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      commentsApi.create(taskId, { content }).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.taskComments(taskId) });
      qc.invalidateQueries({ queryKey: queryKeys.taskActivity(taskId) });
      toastUtils.success("نظر ثبت شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useUpdateComment(taskId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      commentId,
      content,
    }: {
      commentId: string;
      content: string;
    }) => commentsApi.update(commentId, { content }).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.taskComments(taskId) });
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useDeleteComment(taskId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (commentId: string) => commentsApi.delete(commentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.taskComments(taskId) });
      toastUtils.success("نظر حذف شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useProjectActivity(projectId: string) {
  return useQuery({
    queryKey: queryKeys.projectActivity(projectId),
    queryFn: async () => {
      const { data } = await activityApi.listByProject(projectId, {
        page_size: 30,
      });
      return data;
    },
    enabled: !!projectId,
  });
}

export function useTaskActivity(taskId: string | null) {
  return useQuery({
    queryKey: queryKeys.taskActivity(taskId ?? ""),
    queryFn: async () => {
      const { data } = await activityApi.listByTask(taskId!, {
        page_size: 20,
      });
      return data;
    },
    enabled: !!taskId,
  });
}
