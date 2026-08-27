import type { TaskStatus, TaskPriority, ProjectRole } from "@/types";

export const TASK_STATUS_CONFIG: Record<
  TaskStatus,
  { label: string; color: string }
> = {
  BACKLOG: { label: "بک‌لاگ", color: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300" },
  TODO: { label: "انجام‌نشده", color: "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" },
  IN_PROGRESS: { label: "در حال انجام", color: "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" },
  IN_REVIEW: { label: "در حال بررسی", color: "bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300" },
  DONE: { label: "انجام‌شده", color: "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300" },
};

export const TASK_PRIORITY_CONFIG: Record<
  TaskPriority,
  { label: string; color: string }
> = {
  LOW: { label: "پایین", color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" },
  MEDIUM: { label: "متوسط", color: "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" },
  HIGH: { label: "بالا", color: "bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400" },
  URGENT: { label: "فوری", color: "bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400" },
};

export const PROJECT_ROLE_CONFIG: Record<
  ProjectRole,
  { label: string; color: string }
> = {
  OWNER: { label: "مالک", color: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300" },
  ADMIN: { label: "مدیر", color: "bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300" },
  MEMBER: { label: "عضو", color: "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" },
  VIEWER: { label: "مشاهده‌گر", color: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300" },
};

export const KANBAN_COLUMNS: TaskStatus[] = [
  "BACKLOG",
  "TODO",
  "IN_PROGRESS",
  "IN_REVIEW",
  "DONE",
];
