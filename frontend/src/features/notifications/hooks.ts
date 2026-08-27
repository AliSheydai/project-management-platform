"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api/notifications";
import { queryKeys } from "@/lib/query-keys";
import { getApiErrorMessage } from "@/lib/api/error";
import { toastUtils } from "@/lib/utils/toast";

export function useNotifications(params?: {
  unread_only?: boolean;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: queryKeys.notifications(params),
    queryFn: async () => {
      const { data } = await notificationsApi.list(params);
      return data;
    },
    refetchInterval: 30_000,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: queryKeys.unreadCount,
    queryFn: async () => {
      const { data } = await notificationsApi.getUnreadCount();
      return data.unread_count;
    },
    refetchInterval: 30_000,
  });
}

export function useMarkNotificationRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: queryKeys.unreadCount });
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useMarkAllNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: queryKeys.unreadCount });
      toastUtils.success("همه اعلان‌ها خوانده شدند");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useDeleteNotification() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: queryKeys.unreadCount });
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}
