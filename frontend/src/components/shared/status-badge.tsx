"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { TaskStatus, TaskPriority, ProjectRole } from "@/types";
import {
  TASK_STATUS_CONFIG,
  TASK_PRIORITY_CONFIG,
  PROJECT_ROLE_CONFIG,
} from "@/lib/constants";

export function TaskStatusBadge({
  status,
  className,
}: {
  status: TaskStatus;
  className?: string;
}) {
  const config = TASK_STATUS_CONFIG[status];
  return (
    <Badge variant="secondary" className={cn(config.color, className)}>
      {config.label}
    </Badge>
  );
}

export function TaskPriorityBadge({
  priority,
  className,
}: {
  priority: TaskPriority;
  className?: string;
}) {
  const config = TASK_PRIORITY_CONFIG[priority];
  return (
    <Badge variant="secondary" className={cn(config.color, className)}>
      {config.label}
    </Badge>
  );
}

export function RoleBadge({
  role,
  className,
}: {
  role: ProjectRole;
  className?: string;
}) {
  const config = PROJECT_ROLE_CONFIG[role];
  return (
    <Badge variant="secondary" className={cn(config.color, className)}>
      {config.label}
    </Badge>
  );
}
