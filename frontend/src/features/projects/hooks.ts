"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "@/lib/api/projects";
import { queryKeys } from "@/lib/query-keys";
import { getApiErrorMessage } from "@/lib/api/error";
import { toastUtils } from "@/lib/utils/toast";

export function useProjects(params?: {
  q?: string;
  is_archived?: boolean;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: queryKeys.projects(params),
    queryFn: async () => {
      const { data } = await projectsApi.list(params);
      return data;
    },
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: queryKeys.project(projectId),
    queryFn: async () => {
      const { data } = await projectsApi.getById(projectId);
      return data;
    },
    enabled: !!projectId,
  });
}

export function useProjectMembers(projectId: string) {
  return useQuery({
    queryKey: queryKeys.projectMembers(projectId),
    queryFn: async () => {
      const { data } = await projectsApi.getMembers(projectId);
      return data;
    },
    enabled: !!projectId,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      projectsApi.create(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toastUtils.success("پروژه ایجاد شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useUpdateProject(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      name?: string;
      description?: string;
      is_archived?: boolean;
    }) => projectsApi.update(projectId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toastUtils.success("پروژه به‌روزرسانی شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (projectId: string) => projectsApi.delete(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toastUtils.success("پروژه حذف شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useAddMember(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { email?: string; user_id?: string; role?: string }) =>
      projectsApi.addMember(projectId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.projectMembers(projectId) });
      qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toastUtils.success("عضو افزوده شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useUpdateMemberRole(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      projectsApi.updateMemberRole(projectId, userId, role).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.projectMembers(projectId) });
      toastUtils.success("نقش به‌روزرسانی شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}

export function useRemoveMember(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) =>
      projectsApi.removeMember(projectId, userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.projectMembers(projectId) });
      qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toastUtils.success("عضو حذف شد");
    },
    onError: (e) => toastUtils.error("خطا", getApiErrorMessage(e)),
  });
}
