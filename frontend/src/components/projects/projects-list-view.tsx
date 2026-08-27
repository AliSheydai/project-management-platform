"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Archive, FolderKanban, Users } from "lucide-react";
import { PageContainer, PageHeader } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  EmptyState,
  ErrorState,
  CardSkeleton,
  SearchInput,
  Pagination,
  ConfirmDialog,
} from "@/components/shared";
import { projectSchema, type ProjectFormData } from "@/lib/validations";
import {
  useProjects,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
} from "@/features/projects/hooks";
import { formatRelativeDate } from "@/lib/dates";
import type { Project } from "@/types";
import { cn } from "@/lib/utils";
import { RoleBadge } from "@/components/shared";

export function ProjectsListView() {
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [showArchived, setShowArchived] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [editProject, setEditProject] = useState<Project | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useProjects({
    q: q || undefined,
    is_archived: showArchived,
    page,
    page_size: 12,
  });
  const createMutation = useCreateProject();
  const deleteMutation = useDeleteProject();

  return (
    <PageContainer>
      <PageHeader
        title="پروژه‌ها"
        description="مدیریت و پیگیری پروژه‌های تیم"
      >
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="size-4" />
          پروژه جدید
        </Button>
      </PageHeader>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchInput
          className="sm:max-w-xs"
          placeholder="جستجوی پروژه..."
          onChange={(value) => {
            setQ(value);
            setPage(1);
          }}
        />
        <Button
          variant={showArchived ? "secondary" : "outline"}
          size="sm"
          onClick={() => {
            setShowArchived((v) => !v);
            setPage(1);
          }}
        >
          <Archive className="size-4" />
          {showArchived ? "بایگانی‌شده‌ها" : "فعال"}
        </Button>
      </div>

      {isError && <ErrorState retry={() => refetch()} />}

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      )}

      {!isLoading && !isError && data && data.items.length === 0 && (
        <EmptyState
          icon={<FolderKanban className="size-6" />}
          title={showArchived ? "پروژه بایگانی‌شده‌ای نیست" : "هنوز پروژه‌ای ندارید"}
          description="اولین پروژه را بسازید و تیم را دعوت کنید"
          action={{
            label: "ایجاد پروژه",
            onClick: () => setCreateOpen(true),
          }}
        />
      )}

      {!isLoading && !isError && data && data.items.length > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {data.items.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onEdit={() => setEditProject(project)}
                onDelete={() => setDeleteId(project.id)}
              />
            ))}
          </div>
          <Pagination
            className="mt-8"
            page={data.page}
            pages={data.pages}
            onPageChange={setPage}
          />
        </>
      )}

      <ProjectFormDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        title="پروژه جدید"
        loading={createMutation.isPending}
        onSubmit={async (values) => {
          await createMutation.mutateAsync(values);
          setCreateOpen(false);
        }}
      />

      {editProject && (
        <EditProjectDialog
          project={editProject}
          open={!!editProject}
          onOpenChange={(open) => !open && setEditProject(null)}
        />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="حذف پروژه"
        description="این عمل غیرقابل بازگشت است. همه تسک‌ها و داده‌های مرتبط حذف می‌شوند."
        confirmLabel="حذف"
        variant="destructive"
        loading={deleteMutation.isPending}
        onConfirm={async () => {
          if (!deleteId) return;
          await deleteMutation.mutateAsync(deleteId);
          setDeleteId(null);
        }}
      />
    </PageContainer>
  );
}

function ProjectCard({
  project,
  onEdit,
  onDelete,
}: {
  project: Project;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <article
      className={cn(
        "group flex flex-col rounded-lg border border-border bg-card p-4 shadow-sm transition-colors hover:border-foreground/15"
      )}
    >
      <Link href={`/projects/${project.id}/overview`} className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-sm font-semibold text-foreground line-clamp-1 group-hover:underline">
            {project.name}
          </h2>
          {project.current_user_role && (
            <RoleBadge role={project.current_user_role} />
          )}
        </div>
        <p className="mt-2 text-sm text-muted-foreground line-clamp-2 min-h-10">
          {project.description || "بدون توضیحات"}
        </p>
        <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Users className="size-3.5" />
            {project.members_count.toLocaleString("fa-IR")}
          </span>
          <span>{formatRelativeDate(project.updated_at)}</span>
          {project.is_archived && (
            <span className="text-amber-600 dark:text-amber-400">بایگانی</span>
          )}
        </div>
      </Link>
      <div className="mt-4 flex gap-2 border-t border-border pt-3">
        <Button variant="outline" size="sm" className="flex-1" onClick={onEdit}>
          ویرایش
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-destructive"
          onClick={onDelete}
        >
          حذف
        </Button>
      </div>
    </article>
  );
}

function ProjectFormDialog({
  open,
  onOpenChange,
  title,
  loading,
  defaultValues,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  loading?: boolean;
  defaultValues?: ProjectFormData;
  onSubmit: (data: ProjectFormData) => Promise<void>;
}) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: defaultValues ?? { name: "", description: "" },
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        onOpenChange(next);
        if (!next) reset(defaultValues ?? { name: "", description: "" });
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (values) => {
            await onSubmit(values);
            reset();
          })}
        >
          <div className="space-y-2">
            <Label htmlFor="name">نام پروژه</Label>
            <Input id="name" {...register("name")} aria-invalid={!!errors.name} />
            {errors.name && (
              <p className="text-xs text-destructive">{errors.name.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">توضیحات</Label>
            <Textarea id="description" rows={3} {...register("description")} />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              انصراف
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "در حال ذخیره..." : "ذخیره"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EditProjectDialog({
  project,
  open,
  onOpenChange,
}: {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const updateMutation = useUpdateProject(project.id);
  return (
    <ProjectFormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="ویرایش پروژه"
      loading={updateMutation.isPending}
      defaultValues={{
        name: project.name,
        description: project.description ?? "",
      }}
      onSubmit={async (values) => {
        await updateMutation.mutateAsync({
          name: values.name,
          description: values.description,
        });
        onOpenChange(false);
      }}
    />
  );
}
