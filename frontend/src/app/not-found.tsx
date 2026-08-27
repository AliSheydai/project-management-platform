import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">۴۰۴</h1>
      <p className="text-muted-foreground">صفحه مورد نظر یافت نشد.</p>
      <Link
        href="/dashboard"
        className="inline-flex items-center justify-center rounded-md bg-primary px-6 h-10 text-xs font-semibold tracking-widest uppercase text-primary-foreground hover:bg-primary/80 transition-colors"
      >
        بازگشت به داشبورد
      </Link>
    </div>
  );
}
