"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Menu,
  Moon,
  Sun,
  Monitor,
  FolderKanban,
  LayoutDashboard,
  Settings,
  Bell,
  LogOut,
} from "lucide-react";
import { useTheme } from "next-themes";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuthStore } from "@/lib/auth/session";
import { toastUtils } from "@/lib/utils/toast";
import { AppBreadcrumbs } from "./breadcrumbs";
import { NotificationBell } from "./notification-bell";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "داشبورد" },
  { href: "/projects", icon: FolderKanban, label: "پروژه‌ها" },
  { href: "/notifications", icon: Bell, label: "اعلان‌ها" },
  { href: "/settings", icon: Settings, label: "تنظیمات" },
];

interface TopBarProps {
  /** Override breadcrumb last-segment label (e.g. dynamic project name) */
  currentLabel?: string;
}

export function TopBar({ currentLabel }: TopBarProps) {
  const { setTheme } = useTheme();
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

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
    <header className="flex h-14 items-center gap-3 border-b border-border bg-background/95 backdrop-blur-sm px-4 lg:px-5 shrink-0 z-10">
      {/* Mobile menu trigger */}
      <Sheet>
        <SheetTrigger className="lg:hidden inline-flex size-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
          <Menu className="size-5" />
          <span className="sr-only">منو</span>
        </SheetTrigger>
        <SheetContent side="right" className="w-64 p-0 bg-sidebar">
          <div className="flex flex-col h-full">
            {/* Mobile logo */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-sidebar-border">
              <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shrink-0">
                <FolderKanban className="size-4" />
              </div>
              <span className="text-sm font-semibold text-sidebar-foreground">
                پرو‌منیجر
              </span>
            </div>
            {/* Mobile nav */}
            <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
              {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
                const isActive =
                  pathname === href || pathname.startsWith(href + "/");
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium",
                      "transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-sidebar-foreground/70"
                    )}
                  >
                    <Icon
                      className={cn(
                        "size-4 shrink-0",
                        isActive
                          ? "text-sidebar-primary"
                          : "text-sidebar-foreground/50"
                      )}
                    />
                    {label}
                  </Link>
                );
              })}
            </nav>
            {/* Mobile user */}
            {user && (
              <div className="p-4 border-t border-sidebar-border">
                <div className="flex items-center gap-3">
                  <Avatar className="size-8 shrink-0">
                    <AvatarImage src={user.avatar_url ?? undefined} />
                    <AvatarFallback className="text-xs bg-primary/10 text-primary">
                      {getInitials(user.first_name, user.last_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-sidebar-foreground truncate">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-[10px] text-muted-foreground truncate">
                      {user.email}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>

      {/* Breadcrumbs */}
      <div className="flex-1 min-w-0 hidden sm:block">
        <AppBreadcrumbs currentLabel={currentLabel} />
      </div>

      {/* Mobile title fallback */}
      <div className="flex-1 min-w-0 sm:hidden">
        <span className="text-sm font-semibold text-foreground truncate block">
          پرو‌منیجر
        </span>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-0.5 shrink-0">
        {/* Theme toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger className="inline-flex size-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
            <Sun className="size-4 dark:hidden" />
            <Moon className="size-4 hidden dark:block" />
            <span className="sr-only">تغییر پوسته</span>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme("light")}>
              <Sun className="size-4 me-2" />
              روشن
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")}>
              <Moon className="size-4 me-2" />
              تاریک
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")}>
              <Monitor className="size-4 me-2" />
              سیستم
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Notifications with badge */}
        <NotificationBell />

        {/* User avatar menu */}
        <DropdownMenu>
          <DropdownMenuTrigger className="ms-1 rounded-full focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 outline-none">
            <Avatar className="size-8 cursor-pointer ring-2 ring-transparent hover:ring-border transition-all duration-150">
              <AvatarImage src={user?.avatar_url ?? undefined} />
              <AvatarFallback className="text-xs bg-primary/10 text-primary">
                {user ? getInitials(user.first_name, user.last_name) : "??"}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52">
            <div className="px-3 py-2.5 border-b border-border">
              <p className="text-sm font-medium leading-none">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-muted-foreground mt-1">{user?.email}</p>
            </div>
            <DropdownMenuItem onClick={() => router.push("/settings/profile")}>
              پروفایل
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push("/settings/appearance")}>
              ظاهر
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} variant="destructive">
              <LogOut className="size-4 me-2" />
              خروج از سیستم
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
