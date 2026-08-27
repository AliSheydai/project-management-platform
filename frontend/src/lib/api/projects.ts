import { apiClient } from "./client";
import type {
  Project,
  ProjectDetail,
  ProjectMember,
  PaginatedResponse,
} from "@/types";

export const projectsApi = {
  list(params?: {
    q?: string;
    is_archived?: boolean;
    page?: number;
    page_size?: number;
  }) {
    return apiClient.get<PaginatedResponse<Project>>("/projects", {
      params,
    });
  },

  getById(projectId: string) {
    return apiClient.get<ProjectDetail>(`/projects/${projectId}`);
  },

  create(data: { name: string; description?: string }) {
    return apiClient.post<Project>("/projects", data);
  },

  update(
    projectId: string,
    data: { name?: string; description?: string; is_archived?: boolean }
  ) {
    return apiClient.patch<Project>(`/projects/${projectId}`, data);
  },

  delete(projectId: string) {
    return apiClient.delete(`/projects/${projectId}`);
  },

  getMembers(projectId: string) {
    return apiClient.get<ProjectMember[]>(`/projects/${projectId}/members`);
  },

  addMember(
    projectId: string,
    data: { email?: string; user_id?: string; role?: string }
  ) {
    return apiClient.post<ProjectMember>(
      `/projects/${projectId}/members`,
      data
    );
  },

  updateMemberRole(projectId: string, userId: string, role: string) {
    return apiClient.patch<ProjectMember>(
      `/projects/${projectId}/members/${userId}`,
      { role }
    );
  },

  removeMember(projectId: string, userId: string) {
    return apiClient.delete(`/projects/${projectId}/members/${userId}`);
  },
};
