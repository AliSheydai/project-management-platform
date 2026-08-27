import { formatDistanceToNow, format, isAfter, isBefore, startOfDay } from "date-fns-jalali";
import { faIR } from "date-fns-jalali/locale";

export function formatRelativeDate(dateStr: string): string {
  try {
    return formatDistanceToNow(new Date(dateStr), {
      addSuffix: true,
      locale: faIR,
    });
  } catch {
    return dateStr;
  }
}

export function formatDate(dateStr: string): string {
  try {
    return format(new Date(dateStr), "yyyy/MM/dd", { locale: faIR });
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr: string): string {
  try {
    return format(new Date(dateStr), "yyyy/MM/dd HH:mm", { locale: faIR });
  } catch {
    return dateStr;
  }
}

export function isOverdue(dateStr: string | null): boolean {
  if (!dateStr) return false;
  try {
    return isBefore(new Date(dateStr), startOfDay(new Date()));
  } catch {
    return false;
  }
}

export function isDueSoon(dateStr: string | null, days = 3): boolean {
  if (!dateStr) return false;
  try {
    const due = new Date(dateStr);
    const now = new Date();
    const soon = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
    return isAfter(due, now) && isBefore(due, soon);
  } catch {
    return false;
  }
}
