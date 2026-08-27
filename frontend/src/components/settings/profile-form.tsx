"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { PageContainer, PageHeader } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { useUpdateProfile } from "@/features/users/hooks";
import { profileSchema, type ProfileFormData } from "@/lib/validations";

export function ProfileForm() {
  const { user } = useAuth();
  const updateProfile = useUpdateProfile();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    values: {
      first_name: user?.first_name ?? "",
      last_name: user?.last_name ?? "",
    },
  });

  if (!user) return null;

  return (
    <PageContainer>
      <PageHeader
        title="پروفایل"
        description="اطلاعات حساب کاربری خود را مدیریت کنید"
      />
      <Card className="max-w-lg">
        <CardContent className="pt-6">
          <form
            className="space-y-5"
            onSubmit={handleSubmit(async (values) => {
              await updateProfile.mutateAsync(values);
            })}
          >
            <div className="space-y-2">
              <Label>ایمیل</Label>
              <Input value={user.email} disabled />
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="first_name">نام</Label>
                <Input id="first_name" {...register("first_name")} />
                {errors.first_name && (
                  <p className="text-xs text-destructive">
                    {errors.first_name.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">نام خانوادگی</Label>
                <Input id="last_name" {...register("last_name")} />
                {errors.last_name && (
                  <p className="text-xs text-destructive">
                    {errors.last_name.message}
                  </p>
                )}
              </div>
            </div>
            <Button
              type="submit"
              disabled={!isDirty || updateProfile.isPending}
            >
              {updateProfile.isPending ? "در حال ذخیره..." : "ذخیره تغییرات"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
