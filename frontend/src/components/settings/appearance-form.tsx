"use client";

import { useTheme } from "next-themes";
import { Monitor, Moon, Sun } from "lucide-react";
import { PageContainer, PageHeader } from "@/components/layout/page-container";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const THEMES = [
  { id: "light", label: "روشن", icon: Sun, description: "پس‌زمینه روشن" },
  { id: "dark", label: "تاریک", icon: Moon, description: "پس‌زمینه تاریک" },
  {
    id: "system",
    label: "سیستم",
    icon: Monitor,
    description: "هماهنگ با سیستم‌عامل",
  },
] as const;

export function AppearanceForm() {
  const { theme, setTheme } = useTheme();

  return (
    <PageContainer>
      <PageHeader
        title="ظاهر"
        description="پوسته روشن، تاریک یا مطابق سیستم"
      />
      <div className="grid max-w-2xl gap-3 sm:grid-cols-3">
        {THEMES.map(({ id, label, icon: Icon, description }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTheme(id)}
            className={cn(
              "rounded-lg border p-4 text-start transition-colors",
              theme === id
                ? "border-foreground bg-muted/50"
                : "border-border hover:border-foreground/30"
            )}
          >
            <Icon className="mb-3 size-5 text-muted-foreground" />
            <p className="text-sm font-medium">{label}</p>
            <p className="mt-1 text-xs text-muted-foreground">{description}</p>
          </button>
        ))}
      </div>
      <Card className="mt-8 max-w-2xl">
        <CardContent className="pt-6 text-sm text-muted-foreground">
          ترجیح پوسته در مرورگر شما ذخیره می‌شود و در بازدیدهای بعدی اعمال
          می‌گردد.
        </CardContent>
      </Card>
    </PageContainer>
  );
}
