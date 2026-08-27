import { apiClient } from "./client";
import type { NotificationListResponse, UnreadCountResponse } from "@/types";

export const notificationsApi = {
  list(params?: {
    unread_only?: boolean;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get<NotificationListResponse>("/notifications", {
      params,
    });
  },

  getUnreadCount() {
    return apiClient.get<UnreadCountResponse>("/notifications/unread-count");
  },

  markAsRead(notificationId: string) {
    return apiClient.patch(`/notifications/${notificationId}/read`);
  },

  markAllAsRead() {
    return apiClient.post<{ message: string; updated_count: number }>(
      "/notifications/mark-all-read"
    );
  },

  delete(notificationId: string) {
    return apiClient.delete(`/notifications/${notificationId}`);
  },
};
