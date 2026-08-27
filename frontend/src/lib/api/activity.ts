import { apiClient } from "./client";
import type { ActivityLog, PaginatedResponse } from "@/types";

export const activityApi = {
  listByProject(
    projectId: string,
    params?: { page?: number; page_size?: number }
  ) {
    return apiClient.get<PaginatedResponse<ActivityLog>>(
      `/projects/${projectId}/activity`,
      { params }
    );
  },

  listByTask(taskId: string, params?: { page?: number; page_size?: number }) {
    return apiClient.get<PaginatedResponse<ActivityLog>>(
      `/tasks/${taskId}/activity`,
      { params }
    );
  },
};
