import { apiClient } from "./client";
import type { Label } from "@/types";

export const labelsApi = {
  list(projectId: string) {
    return apiClient.get<{ items: Label[]; total: number }>(
      `/projects/${projectId}/labels`
    );
  },

  create(
    projectId: string,
    data: { name: string; color?: string; description?: string }
  ) {
    return apiClient.post<Label>(`/projects/${projectId}/labels`, data);
  },

  update(
    labelId: string,
    data: { name?: string; color?: string; description?: string }
  ) {
    return apiClient.patch<Label>(`/labels/${labelId}`, data);
  },

  delete(labelId: string) {
    return apiClient.delete(`/labels/${labelId}`);
  },

  attachToTask(taskId: string, labelId: string) {
    return apiClient.post(`/tasks/${taskId}/labels/${labelId}`);
  },

  detachFromTask(taskId: string, labelId: string) {
    return apiClient.delete(`/tasks/${taskId}/labels/${labelId}`);
  },
};
