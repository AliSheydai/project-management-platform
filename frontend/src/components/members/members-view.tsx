"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus } from "lucide-react";
import { PageContainer } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  ConfirmDialog,
  EmptyState,
  ErrorState,
  LoadingSkeleton,
  RoleBadge,
  UserAvatar,
} from "@/components/shared";
import {
  useAddMember,
  useProject,
  useProjectMembers,
  useRemoveMember,
  useUpdateMemberRole,
} from "@/features/projects/hooks";
import {
  canChangeRoles,
  canInviteMembers,
} from "@/lib/permissions";
import {
  inviteMemberSchema,
  type InviteMemberFormData,
} from "@/lib/validations";
import { PROJECT_ROLE_CONFIG } from "@/lib/constants";
import type { ProjectRole } from "@/types";

export function MembersView({ projectId }: { projectId: string }) {
  const { data: project } = useProject(projectId);
  const { data, isLoading, isError, refetch } = useProjectMembers(projectId);
  const addMember = useAddMember(projectId);
  const updateRole = useUpdateMemberRole(projectId);
  const removeMember = useRemoveMember(projectId);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [removeUserId, setRemoveUserId] = useState<string | null>(null);

  const canInvite = canInviteMembers(project?.current_user_role);
  const canRole = canChangeRoles(project?.current_user_role);

  const form = useForm<InviteMemberFormData>({
    resolver: zodResolver(inviteMemberSchema),
    defaultValues: { email: "", role: "MEMBER" },
  });

  return (
    <PageContainer>
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold">اعضای پروژه</h2>
          <p className="text-sm text-muted-foreground">
            مدیریت نقش‌ها و دعوت اعضای جدید
          </p>
        </div>
        {canInvite && (
          <Button onClick={() => setInviteOpen(true)}>
            <UserPlus className="size-4" />
            دعوت عضو
          </Button>
        )}
      </div>

      {isLoading && <LoadingSkeleton count={4} />}
      {isError && <ErrorState retry={() => refetch()} />}

      {!isLoading && !isError && data && data.length === 0 && (
        <EmptyState title="عضوی یافت نشد" />
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <ul className="divide-y divide-border rounded-lg border border-border">
          {data.map((member) => (
            <li
              key={member.id}
              className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="flex items-center gap-3 min-w-0">
                <UserAvatar
                  name={member.user.full_name}
                  avatarUrl={member.user.avatar_url}
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">
                    {member.user.full_name}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {member.user.email}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {canRole && member.role !== "OWNER" ? (
                  <select
                    className="h-9 border-0 border-b border-input bg-transparent text-sm"
                    value={member.role}
                    onChange={(e) =>
                      updateRole.mutate({
                        userId: member.user_id,
                        role: e.target.value,
                      })
                    }
                  >
                    {(["ADMIN", "MEMBER", "VIEWER"] as ProjectRole[]).map(
                      (role) => (
                        <option key={role} value={role}>
                          {PROJECT_ROLE_CONFIG[role].label}
                        </option>
                      )
                    )}
                  </select>
                ) : (
                  <RoleBadge role={member.role} />
                )}
                {canInvite && member.role !== "OWNER" && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive"
                    onClick={() => setRemoveUserId(member.user_id)}
                  >
                    حذف
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>دعوت عضو</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={form.handleSubmit(async (values) => {
              await addMember.mutateAsync({
                email: values.email,
                role: values.role,
              });
              form.reset();
              setInviteOpen(false);
            })}
          >
            <div className="space-y-2">
              <Label htmlFor="invite-email">ایمیل</Label>
              <Input id="invite-email" {...form.register("email")} />
              {form.formState.errors.email && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.email.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-role">نقش</Label>
              <select
                id="invite-role"
                className="h-10 w-full border-0 border-b border-input bg-transparent text-sm"
                {...form.register("role")}
              >
                <option value="ADMIN">مدیر</option>
                <option value="MEMBER">عضو</option>
                <option value="VIEWER">مشاهده‌گر</option>
              </select>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setInviteOpen(false)}
              >
                انصراف
              </Button>
              <Button type="submit" disabled={addMember.isPending}>
                {addMember.isPending ? "در حال ارسال..." : "دعوت"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!removeUserId}
        onOpenChange={(open) => !open && setRemoveUserId(null)}
        title="حذف عضو"
        description="این کاربر از پروژه حذف می‌شود."
        confirmLabel="حذف"
        variant="destructive"
        loading={removeMember.isPending}
        onConfirm={async () => {
          if (!removeUserId) return;
          await removeMember.mutateAsync(removeUserId);
          setRemoveUserId(null);
        }}
      />
    </PageContainer>
  );
}
