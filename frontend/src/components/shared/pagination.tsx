"use client";

import { Button } from "@/components/ui/button";
import { ChevronRightIcon, ChevronLeftIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  page,
  pages,
  onPageChange,
  className,
}: PaginationProps) {
  if (pages <= 1) return null;

  return (
    <div className={cn("flex items-center justify-center gap-1", className)}>
      <Button
        variant="outline"
        size="icon-sm"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="صفحه قبل"
      >
        <ChevronRightIcon className="size-4" />
      </Button>
      <span className="px-3 text-sm text-muted-foreground">
        صفحه {page} از {pages}
      </span>
      <Button
        variant="outline"
        size="icon-sm"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= pages}
        aria-label="صفحه بعد"
      >
        <ChevronLeftIcon className="size-4" />
      </Button>
    </div>
  );
}
