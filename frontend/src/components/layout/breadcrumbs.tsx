"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Fragment } from "react";

/**
 * Mapping of URL segments to Persian labels.
 * Dynamic segments (e.g. projectId) are handled separately.
 */
const SEGMENT_LABELS: Record<string, string> = {
  dashboard: "داشبورد",
  projects: "پروژه‌ها",
  notifications: "اعلان‌ها",
  settings: "تنظیمات",
  profile: "پروفایل",
  appearance: "ظاهر",
  overview: "نمای کلی",
  tasks: "تسک‌ها",
  members: "اعضا",
  activity: "فعالیت‌ها",
};

interface AppBreadcrumbsProps {
  /** Override the last segment label (e.g. with a dynamic project name) */
  currentLabel?: string;
}

export function AppBreadcrumbs({ currentLabel }: AppBreadcrumbsProps) {
  const pathname = usePathname();

  // Split path into segments, filter empty
  const segments = pathname.split("/").filter(Boolean);

  // Build cumulative paths for links
  const crumbs = segments.map((seg, i) => ({
    segment: seg,
    href: "/" + segments.slice(0, i + 1).join("/"),
    label: SEGMENT_LABELS[seg] ?? (seg.length > 24 ? `${seg.slice(0, 8)}…` : seg),
    isLast: i === segments.length - 1,
  }));

  if (crumbs.length === 0) return null;

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {crumbs.map((crumb, idx) => (
          <Fragment key={crumb.href}>
            {idx > 0 && <BreadcrumbSeparator className="rtl-flip" />}
            <BreadcrumbItem>
              {crumb.isLast ? (
                <BreadcrumbPage>
                  {currentLabel ?? crumb.label}
                </BreadcrumbPage>
              ) : (
                <BreadcrumbLink
                  render={
                    <Link href={crumb.href} className="hover:text-foreground transition-colors" />
                  }
                >
                  {crumb.label}
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
          </Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
