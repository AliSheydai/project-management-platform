"use client";

import { useMutation } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";
import { useAuthStore } from "@/lib/auth/session";
import { getApiErrorMessage } from "@/lib/api/error";
import { toastUtils } from "@/lib/utils/toast";

export function useUpdateProfile() {
  const setUser = useAuthStore((s) => s.setUser);
  return useMutation({
    mutationFn: (data: {
      first_name?: string;
      last_name?: string;
      avatar_url?: string;
      password?: string;
    }) => usersApi.updateMe(data).then((r) => r.data),
    onSuccess: (user) => {
      setUser(user);
      toastUtils.success("پروفایل به‌روزرسانی شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}
