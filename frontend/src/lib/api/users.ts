import { apiClient } from "./client";
import type { User, PaginatedResponse } from "@/types";

export const usersApi = {
  getMe() {
    return apiClient.get<User>("/users/me");
  },

  updateMe(data: {
    first_name?: string;
    last_name?: string;
    avatar_url?: string;
    password?: string;
  }) {
    return apiClient.patch<User>("/users/me", data);
  },

  getById(userId: string) {
    return apiClient.get<User>(`/users/${userId}`);
  },

  search(params?: { q?: string; page?: number; page_size?: number }) {
    return apiClient.get<PaginatedResponse<User>>("/users", { params });
  },
};
