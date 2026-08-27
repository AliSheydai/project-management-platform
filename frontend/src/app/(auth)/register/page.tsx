import type { Metadata } from "next";
import { RegisterForm } from "@/components/auth/register-form";
import { AuthRedirect } from "@/components/auth/auth-redirect";

export const metadata: Metadata = {
  title: "ثبت‌نام",
};

export default function RegisterPage() {
  return (
    <AuthRedirect>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          پرو‌منیجر
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          ساخت حساب و شروع همکاری تیمی
        </p>
      </div>
      <RegisterForm />
    </AuthRedirect>
  );
}
