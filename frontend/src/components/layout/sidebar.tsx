"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FolderKanban,
  Bell,
  Settings,
  ChevronRight,
  LogOut,
  User,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useAuthStore } from "@/lib/auth/session";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toastUtils } from "@/lib/utils/toast";
import { useSidebar } from "./app-shell";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "داشبورد" },
  { href: "/projects", icon: FolderKanban, label: "پروژه‌ها" },
  { href: "/notifications", icon: Bell, label: "اعلان‌ها" },
  { href: "/settings", icon: Settings, label: "تنظیمات" },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const { collapsed, toggle } = useSidebar();

  const handleLogout = async () => {
    try {
      await logout();
      router.replace("/login");
    } catch {
      toastUtils.error("خطا در خروج از سیستم");
    }
  };

  const getInitials = (firstName: string, lastName: string) =>
    `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();

  return (
    <aside
      className={cn(
        "hidden lg:flex flex-col border-e border-sidebar-border bg-sidebar shrink-0",
        "transition-all duration-200 ease-smooth",
        collapsed ? "w-16" : "w-60",
        className
      )}
    >
      {/* Logo + collapse toggle */}
      <div
        className={cn(
          "flex items-center border-b border-sidebar-border shrink-0",
          "h-14", // same height as top-bar
          collapsed ? "justify-center px-3" : "px-4 gap-3"
        )}
      >
        {!collapsed && (
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shrink-0">
            <FolderKanban className="size-4" />
          </div>
        )}

        {!collapsed && (
          <div className="flex flex-col leading-tight min-w-0 flex-1">
            <span className="text-sm font-semibold text-sidebar-foreground truncate">
              پرو‌منیجر
            </span>
            <span className="text-xs text-muted-foreground">مدیریت پروژه</span>
          </div>
        )}

        <button
          onClick={toggle}
          aria-label={collapsed ? "باز کردن منو" : "بستن منو"}
          className={cn(
            "inline-flex items-center justify-center rounded-md",
            "text-sidebar-foreground/50 hover:text-sidebar-foreground",
            "hover:bg-sidebar-accent transition-colors p-1.5",
            collapsed && "size-9"
          )}
        >
          {collapsed ? (
            <PanelLeftOpen className="size-4 rtl-flip" />
          ) : (
            <PanelLeftClose className="size-4 rtl-flip" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto overflow-x-hidden">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");

          const linkContent = (
            <Link
              key={href}
              href={href}
              className={cn(
                "group flex items-center rounded-md",
                "transition-colors duration-150",
                "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                collapsed
                  ? "justify-center size-10 mx-auto"
                  : "gap-3 px-3 py-2",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70"
              )}
            >
              <Icon
                className={cn(
                  "size-4 shrink-0 transition-colors",
                  isActive
                    ? "text-sidebar-primary"
                    : "text-sidebar-foreground/50 group-hover:text-sidebar-accent-foreground"
                )}
              />
              {!collapsed && (
                <>
                  <span className="flex-1 text-sm font-medium">{label}</span>
                  {isActive && (
                    <ChevronRight className="size-3.5 text-sidebar-primary rtl-flip" />
                  )}
                </>
              )}
            </Link>
          );

          if (collapsed) {
            return (
              <Tooltip key={href}>
                <TooltipTrigger className="w-full flex">
                  {linkContent}
                </TooltipTrigger>
                <TooltipContent side="left" sideOffset={8}>
                  {label}
                </TooltipContent>
              </Tooltip>
            );
          }

          return linkContent;
        })}
      </nav>

      {/* User Profile footer */}
      <div className="p-2 border-t border-sidebar-border shrink-0">
        <DropdownMenu>
          <DropdownMenuTrigger
            className={cn(
              "w-full flex items-center rounded-md",
              "text-sidebar-foreground/70 hover:text-sidebar-accent-foreground",
              "hover:bg-sidebar-accent transition-colors cursor-pointer",
              collapsed ? "justify-center p-2" : "gap-3 px-3 py-2"
            )}
          >
            <Avatar className="size-7 shrink-0">
              <AvatarImage src={user?.avatar_url ?? undefined} />
              <AvatarFallback className="text-xs bg-primary/10 text-primary">
                {user ? getInitials(user.first_name, user.last_name) : "??"}
              </AvatarFallback>
            </Avatar>
            {!collapsed && (
              <div className="flex-1 text-start overflow-hidden">
                <p className="text-xs font-medium truncate text-sidebar-foreground">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-[10px] text-muted-foreground truncate">
                  {user?.email}
                </p>
              </div>
            )}
          </DropdownMenuTrigger>

          <DropdownMenuContent
            side={collapsed ? "right" : "top"}
            align="start"
            className="w-52"
          >
            <DropdownMenuLabel>
              <div className="flex flex-col">
                <span className="text-sm font-medium">
                  {user?.first_name} {user?.last_name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {user?.email}
                </span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push("/settings/profile")}>
              <User className="size-4 me-2" />
              پروفایل
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push("/settings")}>
              <Settings className="size-4 me-2" />
              تنظیمات
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} variant="destructive">
              <LogOut className="size-4 me-2" />
              خروج از سیستم
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
