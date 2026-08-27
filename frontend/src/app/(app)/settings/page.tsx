import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "تنظیمات",
};

export default function SettingsPage() {
  redirect("/settings/profile");
}
