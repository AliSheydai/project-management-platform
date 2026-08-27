import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("ایمیل نامعتبر است"),
  password: z.string().min(1, "رمز عبور الزامی است"),
});

export const registerSchema = z.object({
  email: z.string().email("ایمیل نامعتبر است"),
  password: z
    .string()
    .min(8, "رمز عبور باید حداقل ۸ کاراکتر باشد")
    .max(128, "رمز عبور نباید بیشتر از ۱۲۸ کاراکتر باشد"),
  first_name: z
    .string()
    .min(1, "نام الزامی است")
    .max(100, "نام نباید بیشتر از ۱۰۰ کاراکتر باشد"),
  last_name: z
    .string()
    .min(1, "نام خانوادگی الزامی است")
    .max(100, "نام خانوادگی نباید بیشتر از ۱۰۰ کاراکتر باشد"),
});

export const projectSchema = z.object({
  name: z
    .string()
    .min(1, "نام پروژه الزامی است")
    .max(150, "نام پروژه نباید بیشتر از ۱۵۰ کاراکتر باشد"),
  description: z
    .string()
    .max(2000, "توضیحات نباید بیشتر از ۲۰۰۰ کاراکتر باشد")
    .optional(),
});

export const taskSchema = z.object({
  title: z
    .string()
    .min(1, "عنوان تسک الزامی است")
    .max(200, "عنوان تسک نباید بیشتر از ۲۰۰ کاراکتر باشد"),
  description: z
    .string()
    .max(10000, "توضیحات نباید بیشتر از ۱۰۰۰۰ کاراکتر باشد")
    .optional(),
  status: z.enum(["BACKLOG", "TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"]).optional(),
  priority: z.enum(["LOW", "MEDIUM", "HIGH", "URGENT"]).optional(),
  assignee_id: z.string().uuid().optional().nullable(),
  due_date: z.string().optional().nullable(),
});

export const commentSchema = z.object({
  content: z
    .string()
    .min(1, "متن نظر الزامی است")
    .max(5000, "متن نظر نباید بیشتر از ۵۰۰۰ کاراکتر باشد"),
});

export const inviteMemberSchema = z.object({
  email: z.string().email("ایمیل نامعتبر است"),
  role: z.enum(["ADMIN", "MEMBER", "VIEWER"]).optional(),
});

export const profileSchema = z.object({
  first_name: z
    .string()
    .min(1, "نام الزامی است")
    .max(100, "نام نباید بیشتر از ۱۰۰ کاراکتر باشد"),
  last_name: z
    .string()
    .min(1, "نام خانوادگی الزامی است")
    .max(100, "نام خانوادگی نباید بیشتر از ۱۰۰ کاراکتر باشد"),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ProjectFormData = z.infer<typeof projectSchema>;
export type TaskFormData = z.infer<typeof taskSchema>;
export type CommentFormData = z.infer<typeof commentSchema>;
export type InviteMemberFormData = z.infer<typeof inviteMemberSchema>;
export type ProfileFormData = z.infer<typeof profileSchema>;
