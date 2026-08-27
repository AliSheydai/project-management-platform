import { apiClient } from "./client";
import type { Attachment } from "@/types";

export const attachmentsApi = {
  list(taskId: string) {
    return apiClient.get<{ items: Attachment[]; total: number }>(
      `/tasks/${taskId}/attachments`
    );
  },

  upload(taskId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<Attachment>(`/tasks/${taskId}/attachments`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  download(attachmentId: string) {
    return apiClient.get(`/attachments/${attachmentId}/download`, {
      responseType: "blob",
    });
  },

  delete(attachmentId: string) {
    return apiClient.delete(`/attachments/${attachmentId}`);
  },
};
