import { apiClient } from "./client";
import type { TaskSearchResponse, SavedView } from "@/types";

export const searchApi = {
  searchTasks(params?: {
    q?: string;
    project_id?: string;
    status?: string[];
    priority?: string[];
    assignee_id?: string;
    creator_id?: string;
    label_id?: string;
    unassigned?: boolean;
    due_date_from?: string;
    due_date_to?: string;
    sort_by?: string;
    order?: "asc" | "desc";
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get<TaskSearchResponse>("/search/tasks", { params });
  },

  getSavedViews(projectId?: string) {
    return apiClient.get<{ items: SavedView[]; total: number }>(
      "/saved-views",
      { params: { project_id: projectId } }
    );
  },

  createSavedView(data: {
    name: string;
    project_id?: string;
    filters: Record<string, unknown>;
    is_default?: boolean;
  }) {
    return apiClient.post<SavedView>("/saved-views", data);
  },

  updateSavedView(
    viewId: string,
    data: { name?: string; filters?: Record<string, unknown>; is_default?: boolean }
  ) {
    return apiClient.patch<SavedView>(`/saved-views/${viewId}`, data);
  },

  deleteSavedView(viewId: string) {
    return apiClient.delete(`/saved-views/${viewId}`);
  },
};
