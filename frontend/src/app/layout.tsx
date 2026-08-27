import type { Metadata } from "next";
import { Vazirmatn } from "next/font/google";
import { Providers } from "@/providers";
import "./globals.css";

const vazirmatn = Vazirmatn({
  subsets: ["arabic"],
  variable: "--font-vazirmatn",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "پلتفرم مدیریت پروژه",
    template: "%s | پلتفرم مدیریت پروژه",
  },
  description:
    "پلتفرم حرفه‌ای مدیریت پروژه و تیم — وظایف، پروژه‌ها، اعلان‌ها و همکاری در یک مکان",
  keywords: ["مدیریت پروژه", "مدیریت وظایف", "همکاری تیمی"],
  authors: [{ name: "Engineering Team" }],
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    locale: "fa_IR",
    siteName: "پلتفرم مدیریت پروژه",
    title: "پلتفرم مدیریت پروژه",
    description: "پلتفرم حرفه‌ای مدیریت پروژه و تیم",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl" className={vazirmatn.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-vazirmatn antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
