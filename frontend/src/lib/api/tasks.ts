import { apiClient } from "./client";
import type { Task, PaginatedResponse } from "@/types";

export const tasksApi = {
  list(
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
    return apiClient.get<PaginatedResponse<Task>>(
      `/projects/${projectId}/tasks`,
      { params }
    );
  },

  getById(taskId: string) {
    return apiClient.get<Task>(`/tasks/${taskId}`);
  },

  create(
    projectId: string,
    data: {
      title: string;
      description?: string;
      status?: string;
      priority?: string;
      assignee_id?: string;
      due_date?: string;
      position?: number;
      label_ids?: string[];
    }
  ) {
    return apiClient.post<Task>(`/projects/${projectId}/tasks`, data);
  },

  update(
    taskId: string,
    data: {
      title?: string;
      description?: string;
      status?: string;
      priority?: string;
      assignee_id?: string;
      unassign?: boolean;
      due_date?: string;
      clear_due_date?: boolean;
      position?: number;
      label_ids?: string[];
    }
  ) {
    return apiClient.patch<Task>(`/tasks/${taskId}`, data);
  },

  reorder(taskId: string, data: { position: number; status?: string }) {
    return apiClient.patch<Task>(`/tasks/${taskId}/reorder`, data);
  },

  delete(taskId: string) {
    return apiClient.delete(`/tasks/${taskId}`);
  },
};
