"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useProject } from "@/features/projects/hooks";
import { ErrorState, LoadingSkeleton } from "@/components/shared";
import { PageContainer } from "@/components/layout/page-container";

const TABS = [
  { href: "overview", label: "نمای کلی" },
  { href: "tasks", label: "تسک‌ها" },
  { href: "members", label: "اعضا" },
  { href: "activity", label: "فعالیت‌ها" },
] as const;

export function ProjectLayoutShell({
  projectId,
  children,
}: {
  projectId: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { data: project, isLoading, isError, refetch } = useProject(projectId);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingSkeleton count={4} />
      </PageContainer>
    );
  }

  if (isError || !project) {
    return (
      <PageContainer>
        <ErrorState
          title="پروژه یافت نشد"
          description="ممکن است حذف شده باشد یا دسترسی نداشته باشید."
          retry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border bg-background/95 px-4 pt-5 sm:px-6 lg:px-8">
        <div className="mb-4">
          <h1 className="text-xl font-semibold tracking-tight">{project.name}</h1>
          {project.description && (
            <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
              {project.description}
            </p>
          )}
        </div>
        <nav className="flex gap-1 overflow-x-auto" aria-label="بخش‌های پروژه">
          {TABS.map((tab) => {
            const href = `/projects/${projectId}/${tab.href}`;
            const active = pathname.includes(`/${tab.href}`);
            return (
              <Link
                key={tab.href}
                href={href}
                className={cn(
                  "shrink-0 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors",
                  active
                    ? "border-foreground text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
