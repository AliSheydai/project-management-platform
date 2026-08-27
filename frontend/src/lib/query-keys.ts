export const queryKeys = {
  currentUser: ["current-user"] as const,
  projects: (filters?: Record<string, unknown>) =>
    ["projects", filters ?? {}] as const,
  project: (id: string) => ["project", id] as const,
  projectMembers: (id: string) => ["project-members", id] as const,
  projectTasks: (id: string, filters?: Record<string, unknown>) =>
    ["project-tasks", id, filters ?? {}] as const,
  task: (id: string) => ["task", id] as const,
  taskComments: (id: string) => ["task-comments", id] as const,
  projectActivity: (id: string) => ["project-activity", id] as const,
  taskActivity: (id: string) => ["task-activity", id] as const,
  notifications: (filters?: Record<string, unknown>) =>
    ["notifications", filters ?? {}] as const,
  unreadCount: ["notifications-unread-count"] as const,
  searchTasks: (filters?: Record<string, unknown>) =>
    ["search-tasks", filters ?? {}] as const,
  projectLabels: (id: string) => ["project-labels", id] as const,
};
