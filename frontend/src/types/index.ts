export type ProjectRole = "OWNER" | "ADMIN" | "MEMBER" | "VIEWER";

export type TaskStatus =
  | "BACKLOG"
  | "TODO"
  | "IN_PROGRESS"
  | "IN_REVIEW"
  | "DONE";

export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export type NotificationType =
  | "task:assigned"
  | "task:status_changed"
  | "comment:added"
  | "user:mentioned"
  | "project:invited";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  tokens: TokenResponse;
  user: User;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  current_user_role: ProjectRole | null;
  members_count: number;
}

export interface ProjectMember {
  id: string;
  project_id: string;
  user_id: string;
  role: ProjectRole;
  user: User;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  owner: User;
  members: ProjectMember[];
}

export interface Label {
  id: string;
  project_id: string;
  name: string;
  color: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id: string | null;
  creator_id: string;
  due_date: string | null;
  position: number;
  custom_fields: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  creator: User;
  assignee: User | null;
  labels: Label[];
}

export interface Comment {
  id: string;
  task_id: string;
  author_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: User;
}

export interface Notification {
  id: string;
  user_id: string;
  actor_id: string | null;
  type: string;
  title: string;
  message: string;
  entity_type: string;
  entity_id: string;
  payload: Record<string, unknown> | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  actor: User | null;
}

export interface ActivityLog {
  id: string;
  project_id: string;
  task_id: string | null;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, unknown> | null;
  created_at: string;
  user: User;
}

export interface Attachment {
  id: string;
  task_id: string;
  uploader_id: string;
  file_name: string;
  file_size: number;
  content_type: string;
  created_at: string;
  uploader: User | null;
}

export interface SavedView {
  id: string;
  user_id: string;
  project_id: string | null;
  name: string;
  filters: Record<string, unknown>;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface NotificationListResponse
  extends PaginatedResponse<Notification> {
  unread_count: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface TaskSearchResponse extends PaginatedResponse<Task> {
  facets: {
    status_counts: Record<string, number>;
    priority_counts: Record<string, number>;
  };
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: unknown | null;
  };
}
