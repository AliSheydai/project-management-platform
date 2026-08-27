import { AxiosError } from "axios";
import type { ApiError } from "@/types";

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiError | undefined;
    if (data?.error?.message) {
      return data.error.message;
    }
    if (error.response?.status === 401) {
      return "نشست شما منقضی شده است. لطفاً دوباره وارد شوید.";
    }
    if (error.response?.status === 403) {
      return "شما دسترسی لازم برای این عملیات را ندارید.";
    }
    if (error.response?.status === 404) {
      return "منبع مورد نظر یافت نشد.";
    }
    if (error.response?.status === 409) {
      return "این مورد قبلاً وجود دارد.";
    }
    if (error.response?.status === 422) {
      return "اطلاعات وارد شده نامعتبر است.";
    }
    if (error.response?.status === 429) {
      return "تعداد درخواست‌ها زیاد است. لطفاً کمی صبر کنید.";
    }
    if (error.response?.status === 500) {
      return "خطای سرور. لطفاً بعداً تلاش کنید.";
    }
    if (!error.response) {
      return "خطا در اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید.";
    }
  }
  return "خطای غیرمنتظره‌ای رخ داد.";
}

export function getApiErrorCode(error: unknown): string | null {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiError | undefined;
    return data?.error?.code ?? null;
  }
  return null;
}
