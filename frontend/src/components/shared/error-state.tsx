"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { AlertCircleIcon } from "lucide-react";

interface ErrorStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  retry?: () => void;
  className?: string;
}

export function ErrorState({
  icon,
  title = "خطایی رخ داد",
  description = "مجدداً تلاش کنید.",
  retry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 text-center",
        className
      )}
    >
      <div className="flex size-12 items-center justify-center rounded-full bg-destructive/10 text-destructive mb-4">
        {icon || <AlertCircleIcon className="size-6" />}
      </div>
      <h3 className="text-sm font-medium text-foreground">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground max-w-sm">
        {description}
      </p>
      {retry && (
        <Button onClick={retry} variant="outline" className="mt-4" size="sm">
          تلاش مجدد
        </Button>
      )}
    </div>
  );
}
