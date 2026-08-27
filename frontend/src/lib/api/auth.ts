import { apiClient } from "./client";
import type { AuthResponse, User } from "@/types";

export const authApi = {
  register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    avatar_url?: string;
  }) {
    return apiClient.post<AuthResponse>("/auth/register", data);
  },

  login(data: { email: string; password: string }) {
    return apiClient.post<AuthResponse>("/auth/login", data);
  },

  refresh(refreshToken: string) {
    return apiClient.post<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    }>("/auth/refresh", { refresh_token: refreshToken });
  },

  logout(refreshToken: string) {
    return apiClient.post<{ message: string }>("/auth/logout", {
      refresh_token: refreshToken,
    });
  },

  me() {
    return apiClient.get<User>("/auth/me");
  },
};
