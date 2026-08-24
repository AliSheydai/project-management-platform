# 📖 API Documentation

All API endpoints are versioned under `/api/v1` and follow RESTful design standards.

---

## 🔒 Authentication & Session Endpoints

Base URL: `/api/v1/auth`

### 1. Register User
* **Method**: `POST`
* **Path**: `/api/v1/auth/register`
* **Status**: `201 Created`
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "first_name": "Jane",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatar.png"
  }
  ```
* **Response Body**: Returns `AuthResponse` with JWT token pair and safe `user` profile.

---

### 2. Login User
* **Method**: `POST`
* **Path**: `/api/v1/auth/login`
* **Status**: `200 OK`
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }
  ```
* **Response Body**: Returns `AuthResponse` with fresh `tokens` and `user` profile.

---

### 3. Refresh Token
* **Method**: `POST`
* **Path**: `/api/v1/auth/refresh`
* **Status**: `200 OK`
* **Request Body**:
  ```json
  {
    "refresh_token": "kG9a..."
  }
  ```
* **Response Body**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "mZ4p...",
    "token_type": "bearer",
    "expires_in": 1800
  }
  ```
* **Notes**: Uses **Token Rotation** — the previous refresh token is immediately invalidated upon issuance of the new token pair.

---

### 4. Logout User
* **Method**: `POST`
* **Path**: `/api/v1/auth/logout`
* **Status**: `200 OK`
* **Request Body**:
  ```json
  {
    "refresh_token": "kG9a..."
  }
  ```
* **Response Body**:
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

---

### 5. Get Current User Profile
* **Method**: `GET`
* **Path**: `/api/v1/auth/me`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Response Body**: Returns `UserResponse` for authenticated active user.

---

## 👤 User Profile & Directory Endpoints

Base URL: `/api/v1/users`

### 1. Get Current User Profile
* **Method**: `GET`
* **Path**: `/api/v1/users/me`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Response Body**: Returns `UserResponse`

---

### 2. Update Current User Profile
* **Method**: `PATCH`
* **Path**: `/api/v1/users/me`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Request Body**:
  ```json
  {
    "first_name": "Jane",
    "last_name": "Smith",
    "avatar_url": "https://example.com/new_avatar.png",
    "password": "NewSecurePassword123!"
  }
  ```
* **Response Body**: Returns updated `UserResponse`.

---

### 3. Get User Profile by ID
* **Method**: `GET`
* **Path**: `/api/v1/users/{user_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Response Body**: Returns public `UserResponse`.

---

### 4. Search and List Users
* **Method**: `GET`
* **Path**: `/api/v1/users?q={query}&page={page}&page_size={page_size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Response Body**: Returns `UserListResponse` with pagination metadata.

---

## 📁 Projects & Workspace Endpoints

Base URL: `/api/v1/projects`

### 1. Create Project
* **Method**: `POST`
* **Path**: `/api/v1/projects`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `201 Created`
* **Request Body**:
  ```json
  {
    "name": "Design System Redesign",
    "description": "Standardize UI component library and styling"
  }
  ```
* **Response Body**: Returns `ProjectResponse` with `current_user_role: "OWNER"`.

---

### 2. List Projects
* **Method**: `GET`
* **Path**: `/api/v1/projects?q={query}&is_archived={bool}&page={page}&page_size={page_size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Response Body**: Returns `ProjectListResponse`.

---

### 3. Get Project Detail
* **Method**: `GET`
* **Path**: `/api/v1/projects/{project_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW` (all members).
* **Response Body**: Returns `ProjectDetailResponse` with complete `owner` profile and `members` array.

---

### 4. Update Project
* **Method**: `PATCH`
* **Path**: `/api/v1/projects/{project_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_EDIT` (`OWNER` or `ADMIN`).
* **Request Body**:
  ```json
  {
    "name": "Design System v2",
    "description": "Updated roadmap description",
    "is_archived": false
  }
  ```

---

### 5. Delete Project
* **Method**: `DELETE`
* **Path**: `/api/v1/projects/{project_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `204 No Content`
* **Permission**: Requires `PROJECT_DELETE` (`OWNER` only).

---

### 6. List Project Members
* **Method**: `GET`
* **Path**: `/api/v1/projects/{project_id}/members`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW`.
* **Response Body**: Array of `ProjectMemberResponse` objects.

---

### 7. Add / Invite Project Member
* **Method**: `POST`
* **Path**: `/api/v1/projects/{project_id}/members`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `201 Created`
* **Permission**: Requires `MEMBER_INVITE` (`OWNER` or `ADMIN`).
* **Request Body**:
  ```json
  {
    "email": "colleague@example.com",
    "role": "MEMBER"
  }
  ```

---

### 8. Update Member Role
* **Method**: `PATCH`
* **Path**: `/api/v1/projects/{project_id}/members/{user_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `MEMBER_ROLE_CHANGE` (`OWNER` only).
* **Request Body**:
  ```json
  {
    "role": "ADMIN"
  }
  ```

---

### 9. Remove Member or Leave Project
* **Method**: `DELETE`
* **Path**: `/api/v1/projects/{project_id}/members/{user_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Self-removal (leaving) or `MEMBER_REMOVE` (`OWNER` or `ADMIN`).
* **Response Body**:
  ```json
  {
    "message": "Member removed successfully"
  }
  ```

---

## 📋 Tasks & Workflow Endpoints

Base URL: `/api/v1`

### 1. Create Task in Project
* **Method**: `POST`
* **Path**: `/api/v1/projects/{project_id}/tasks`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `201 Created`
* **Permission**: Requires `TASK_CREATE` (`OWNER`, `ADMIN`, `MEMBER`).
* **Request Body**:
  ```json
  {
    "title": "Build Navigation Component",
    "description": "Responsive navbar with RTL support",
    "status": "TODO",
    "priority": "HIGH",
    "assignee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "due_date": "2026-09-01T12:00:00Z"
  }
  ```
* **Response Body**: Returns `TaskResponse` with loaded `creator` and `assignee`.

---

### 2. List & Filter Project Tasks
* **Method**: `GET`
* **Path**: `/api/v1/projects/{project_id}/tasks?status={status}&priority={priority}&assignee_id={uuid}&unassigned={bool}&q={search}&sort_by={col}&order={asc|desc}&page={page}&page_size={size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW` (all project members).
* **Response Body**: Returns `TaskListResponse` with pagination metadata.

---

### 3. Get Task Details
* **Method**: `GET`
* **Path**: `/api/v1/tasks/{task_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW` on task's project.
* **Response Body**: Returns `TaskResponse`.

---

### 4. Update Task
* **Method**: `PATCH`
* **Path**: `/api/v1/tasks/{task_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `TASK_EDIT` (`OWNER`, `ADMIN`, or task assignee / creator `MEMBER`).
* **Request Body**:
  ```json
  {
    "title": "Updated Task Title",
    "status": "IN_PROGRESS",
    "priority": "URGENT",
    "assignee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }
  ```
* **Response Body**: Returns updated `TaskResponse`.

---

### 5. Reorder Task on Kanban / Board
* **Method**: `PATCH`
* **Path**: `/api/v1/tasks/{task_id}/reorder`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `TASK_EDIT`.
* **Request Body**:
  ```json
  {
    "position": 2500.0,
    "status": "DONE"
  }
  ```
* **Response Body**: Returns updated `TaskResponse`.

---

### 6. Delete Task
* **Method**: `DELETE`
* **Path**: `/api/v1/tasks/{task_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `204 No Content`
* **Permission**: Requires `TASK_DELETE` (`OWNER` or `ADMIN`).

---

## 💬 Collaboration Comments Endpoints

Base URL: `/api/v1`

### 1. Add Comment to Task
* **Method**: `POST`
* **Path**: `/api/v1/tasks/{task_id}/comments`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `201 Created`
* **Permission**: Requires `COMMENT_CREATE` (`OWNER`, `ADMIN`, `MEMBER`).
* **Request Body**:
  ```json
  {
    "content": "Updated design tokens according to modern guidelines."
  }
  ```
* **Response Body**: Returns `CommentResponse` with populated `author` profile.

---

### 2. List Task Comments
* **Method**: `GET`
* **Path**: `/api/v1/tasks/{task_id}/comments?page={page}&page_size={page_size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW` (all project members).
* **Response Body**: Returns `CommentListResponse`.

---

### 3. Edit Comment
* **Method**: `PATCH`
* **Path**: `/api/v1/comments/{comment_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Restricted to comment author.
* **Request Body**:
  ```json
  {
    "content": "Edited comment text content"
  }
  ```
* **Response Body**: Returns updated `CommentResponse`.

---

### 4. Delete Comment
* **Method**: `DELETE`
* **Path**: `/api/v1/comments/{comment_id}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `204 No Content`
* **Permission**: Comment author, or `COMMENT_DELETE` (`OWNER` / `ADMIN`).

---

## 📜 Activity Feed & Audit Log Endpoints

Base URL: `/api/v1`

### 1. Get Project Activity Log
* **Method**: `GET`
* **Path**: `/api/v1/projects/{project_id}/activity?page={page}&page_size={page_size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW`.
* **Response Body**: Returns `ActivityListResponse` containing workspace audit trail entries.

---

### 2. Get Task Activity History
* **Method**: `GET`
* **Path**: `/api/v1/tasks/{task_id}/activity?page={page}&page_size={page_size}`
* **Headers**: `Authorization: Bearer <access_token>`
* **Status**: `200 OK`
* **Permission**: Requires `PROJECT_VIEW`.
* **Response Body**: Returns `ActivityListResponse` for the task.

---

## 🛡 Role-Based Access Control (RBAC) Hierarchy

```text
OWNER (Rank 40)
 ├── Manage project & settings
 ├── Invite & remove members
 ├── Change member roles
 ├── Create, edit, delete tasks
 ├── Add / delete all comments
 └── Delete project

ADMIN (Rank 30)
 ├── Manage project & settings
 ├── Invite & remove members (cannot remove owners or admins)
 ├── Create, edit, delete tasks
 └── Add / delete all comments

MEMBER (Rank 20)
 ├── View project & tasks
 ├── Create tasks
 ├── Edit assigned tasks
 └── Add comments (and edit/delete own comments)

VIEWER (Rank 10)
 └── Read-only access to project & tasks
```

---

## ⚠️ Standard Error Format

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Action requires 'task:create' permission, but your project role is 'VIEWER'.",
    "details": null
  }
}
```
