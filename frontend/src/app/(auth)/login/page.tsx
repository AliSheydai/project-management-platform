import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/login-form";
import { AuthRedirect } from "@/components/auth/auth-redirect";

export const metadata: Metadata = {
  title: "ورود",
};

export default function LoginPage() {
  return (
    <AuthRedirect>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          پرو‌منیجر
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          مدیریت پروژه و تیم در یک مکان
        </p>
      </div>
      <LoginForm />
    </AuthRedirect>
  );
}
