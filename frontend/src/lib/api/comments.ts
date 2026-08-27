import { apiClient } from "./client";
import type { Comment, PaginatedResponse } from "@/types";

export const commentsApi = {
  list(taskId: string, params?: { page?: number; page_size?: number }) {
    return apiClient.get<PaginatedResponse<Comment>>(
      `/tasks/${taskId}/comments`,
      { params }
    );
  },

  create(taskId: string, data: { content: string }) {
    return apiClient.post<Comment>(`/tasks/${taskId}/comments`, data);
  },

  update(commentId: string, data: { content: string }) {
    return apiClient.patch<Comment>(`/comments/${commentId}`, data);
  },

  delete(commentId: string) {
    return apiClient.delete(`/comments/${commentId}`);
  },
};
