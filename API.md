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
* **Response Body**:
  ```json
  {
    "tokens": {
      "access_token": "eyJhbGciOi...",
      "refresh_token": "kG9a...",
      "token_type": "bearer",
      "expires_in": 1800
    },
    "user": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "first_name": "Jane",
      "last_name": "Doe",
      "full_name": "Jane Doe",
      "avatar_url": "https://example.com/avatar.png",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2026-08-24T22:00:00Z",
      "updated_at": "2026-08-24T22:00:00Z"
    }
  }
  ```

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
* **Response Body**:
  ```json
  {
    "items": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "email": "user@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "full_name": "Jane Doe",
        "avatar_url": "https://example.com/avatar.png",
        "is_active": true,
        "is_superuser": false,
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

## 🛡 Role-Based Access Control (RBAC) Hierarchy

The platform implements strict server-side authorization:

```text
OWNER (Rank 40)
 ├── Manage project & settings
 ├── Invite & remove members
 ├── Change member roles
 ├── Create, edit, delete tasks
 └── Delete project

ADMIN (Rank 30)
 ├── Manage project & settings
 ├── Invite & remove members
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

All error responses strictly adhere to the unified schema:

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Action requires 'project:edit' permission, but your project role is 'VIEWER'.",
    "details": null
  }
}
```
