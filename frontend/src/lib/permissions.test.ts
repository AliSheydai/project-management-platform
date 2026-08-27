import { describe, expect, it } from "vitest";
import {
  canEditTasks,
  canInviteMembers,
  canManageProject,
  canDeleteProject,
} from "@/lib/permissions";

describe("permissions", () => {
  it("allows OWNER and ADMIN to manage project", () => {
    expect(canManageProject("OWNER")).toBe(true);
    expect(canManageProject("ADMIN")).toBe(true);
    expect(canManageProject("MEMBER")).toBe(false);
    expect(canManageProject("VIEWER")).toBe(false);
    expect(canManageProject(null)).toBe(false);
  });

  it("allows MEMBER+ to edit tasks", () => {
    expect(canEditTasks("MEMBER")).toBe(true);
    expect(canEditTasks("VIEWER")).toBe(false);
  });

  it("restricts invite and delete correctly", () => {
    expect(canInviteMembers("ADMIN")).toBe(true);
    expect(canInviteMembers("MEMBER")).toBe(false);
    expect(canDeleteProject("OWNER")).toBe(true);
    expect(canDeleteProject("ADMIN")).toBe(false);
  });
});
