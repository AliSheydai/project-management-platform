/**
 * Toast utility — thin wrapper around the base-ui ToastManager.
 * Provides a sonner-like API: toast.success(), toast.error(), toast.info()
 */
import { toast as baseToast } from "@/components/ui/toast";

export const toastUtils = {
  success(title: string, description?: string) {
    baseToast.add({ type: "success", title, description });
  },
  error(title: string, description?: string) {
    baseToast.add({ type: "error", title, description });
  },
  info(title: string, description?: string) {
    baseToast.add({ type: "info", title, description });
  },
  warning(title: string, description?: string) {
    baseToast.add({ type: "warning", title, description });
  },
  loading(title: string, description?: string) {
    return baseToast.add({ type: "loading", title, description });
  },
  dismiss(id?: string) {
    if (id) {
      baseToast.close(id);
    }
  },
};
