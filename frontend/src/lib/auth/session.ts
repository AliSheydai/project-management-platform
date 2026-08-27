"use client";

import { create } from "zustand";
import type { User } from "@/types";
import { tokenStore } from "./token";
import { authApi } from "@/lib/api/auth";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  restore: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user) =>
    set({ user, isAuthenticated: !!user, isLoading: false }),

  setLoading: (isLoading) => set({ isLoading }),

  login: async (email, password) => {
    const { data } = await authApi.login({ email, password });
    tokenStore.setTokens(data.tokens.access_token, data.tokens.refresh_token);
    set({ user: data.user, isAuthenticated: true, isLoading: false });
  },

  register: async (registerData) => {
    const { data } = await authApi.register(registerData);
    tokenStore.setTokens(data.tokens.access_token, data.tokens.refresh_token);
    set({ user: data.user, isAuthenticated: true, isLoading: false });
  },

  logout: async () => {
    const refreshToken = tokenStore.getRefreshToken();
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch {
        // ignore logout errors
      }
    }
    tokenStore.clear();
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  restore: async () => {
    const refreshToken = tokenStore.getRefreshToken();
    if (!refreshToken) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const { data } = await authApi.refresh(refreshToken);
      tokenStore.setTokens(data.access_token, data.refresh_token);
      const { data: user } = await authApi.me();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      tokenStore.clear();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
