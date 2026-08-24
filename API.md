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
* **Response Body**:
  ```json
  {
    "items": [
      {
        "id": "7b0b6c6b-f418-4bf8-92c2-8fe26778ba72",
        "name": "Design System Redesign",
        "description": "Standardize UI component library",
        "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "is_archived": false,
        "current_user_role": "OWNER",
        "members_count": 4,
        "created_at": "2026-08-24T22:00:00Z",
        "updated_at": "2026-08-24T22:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "pages": 1
  }
  ```

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

## 🛡 Role-Based Access Control (RBAC) Hierarchy

```text
OWNER (Rank 40)
 ├── Manage project & settings
 ├── Invite & remove members
 ├── Change member roles
 ├── Create, edit, delete tasks
 └── Delete project

ADMIN (Rank 30)
 ├── Manage project & settings
 ├── Invite & remove members (cannot remove owners or admins)
 ├── Create, edit, delete tasks
 └── Add / delete comments

MEMBER (Rank 20)
 ├── View project & tasks
 ├── Create tasks
 ├── Edit assigned tasks
 └── Add comments

VIEWER (Rank 10)
 └── Read-only access to project & tasks
```

---

## ⚠️ Standard Error Format

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Action requires 'project:edit' permission, but your project role is 'VIEWER'.",
    "details": null
  }
}
```
