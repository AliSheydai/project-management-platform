import type { ProjectRole } from "@/types";

const RANK: Record<ProjectRole, number> = {
  OWNER: 4,
  ADMIN: 3,
  MEMBER: 2,
  VIEWER: 1,
};

export function canManageProject(role: ProjectRole | null | undefined) {
  return !!role && RANK[role] >= RANK.ADMIN;
}

export function canEditTasks(role: ProjectRole | null | undefined) {
  return !!role && RANK[role] >= RANK.MEMBER;
}

export function canInviteMembers(role: ProjectRole | null | undefined) {
  return !!role && RANK[role] >= RANK.ADMIN;
}

export function canChangeRoles(role: ProjectRole | null | undefined) {
  return role === "OWNER" || role === "ADMIN";
}

export function canDeleteProject(role: ProjectRole | null | undefined) {
  return role === "OWNER";
}
