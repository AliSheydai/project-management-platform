import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  /** Remove default padding for full-bleed pages (e.g. kanban) */
  noPadding?: boolean;
}

/**
 * Consistent page wrapper with standard padding and max-width.
 * All (app) pages should be wrapped in this.
 */
export function PageContainer({
  children,
  className,
  noPadding = false,
}: PageContainerProps) {
  return (
    <div
      className={cn(
        "w-full h-full",
        !noPadding && "px-4 py-6 sm:px-6 lg:px-8",
        className
      )}
    >
      {children}
    </div>
  );
}

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode; // right-side actions
  className?: string;
}

/**
 * Consistent page header with title, optional description, and action slot.
 */
export function PageHeader({
  title,
  description,
  children,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between mb-6",
        className
      )}
    >
      <div className="min-w-0">
        <h1 className="text-xl font-semibold text-foreground tracking-tight truncate">
          {title}
        </h1>
        {description && (
          <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {children && (
        <div className="flex items-center gap-2 shrink-0 mt-2 sm:mt-0">
          {children}
        </div>
      )}
    </div>
  );
}
