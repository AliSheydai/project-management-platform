import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { tokenStore } from "@/lib/auth/token";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface QueueItem {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}

let isRefreshing = false;
let failedQueue: QueueItem[] = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
}

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`;
        }
        return apiClient(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = tokenStore.getRefreshToken();
    if (!refreshToken) {
      tokenStore.clear();
      processQueue(error, null);
      isRefreshing = false;
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    try {
      const { data } = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      tokenStore.setTokens(data.access_token, data.refresh_token);
      processQueue(null, data.access_token);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      }
      return apiClient(originalRequest);
    } catch (refreshError) {
      tokenStore.clear();
      processQueue(refreshError, null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
