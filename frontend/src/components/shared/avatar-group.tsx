"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import type { User } from "@/types";

interface AvatarGroupProps {
  users: (User | { first_name: string; last_name: string; avatar_url?: string | null })[];
  max?: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "size-6 text-xs",
  md: "size-8 text-sm",
  lg: "size-10 text-base",
};

export function AvatarGroup({
  users,
  max = 4,
  size = "sm",
  className,
}: AvatarGroupProps) {
  const visible = users.slice(0, max);
  const remaining = users.length - max;

  return (
    <div className={cn("flex -space-x-2 space-x-reverse", className)}>
      {visible.map((user, i) => (
        <Avatar
          key={i}
          className={cn(
            sizeClasses[size],
            "ring-2 ring-background"
          )}
        >
          <AvatarImage src={user.avatar_url ?? undefined} />
          <AvatarFallback>
            {user.first_name.charAt(0)}
            {user.last_name.charAt(0)}
          </AvatarFallback>
        </Avatar>
      ))}
      {remaining > 0 && (
        <div
          className={cn(
            sizeClasses[size],
            "flex items-center justify-center rounded-full bg-muted text-muted-foreground ring-2 ring-background"
          )}
        >
          +{remaining}
        </div>
      )}
    </div>
  );
}
