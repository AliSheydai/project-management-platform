# 🏛 Project Architecture Documentation

## 1. Architectural Decisions

### Modular Monolith
The platform is organized as a modular monolith. Modules (`auth`, `users`, `projects`, `tasks`, `comments`, `labels`, `attachments`, `notifications`, `activity`) are encapsulated with explicit models, schemas, repositories, and API routers. This ensures high velocity during early development while maintaining clean domain boundaries for future microservice extraction if needed.

### Asynchronous SQLAlchemy 2.0 & Asyncpg
- **Non-blocking I/O**: Leveraging `asyncpg` and SQLAlchemy's `AsyncEngine`/`AsyncSessionLocal` avoids thread pool saturation during high-throughput I/O.
- **Declarative Base**: `DeclarativeBase` with typed annotations (`Mapped[T]` and `mapped_column`) enforces compile-time and runtime type safety.
- **Mixins**: `UUIDMixin` and `TimestampMixin` standardise primary keys and audit timestamps across all entities.

### Role-Based Access Control (RBAC)
- **Granular Permissions Matrix**: Roles (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`) are mapped to explicit permissions (`PROJECT_VIEW`, `PROJECT_EDIT`, `TASK_CREATE`, `COMMENT_CREATE`, etc.) in `app/core/permissions.py`.
- **FastAPI Dependency Factories**: Permissions are verified before endpoint handlers are invoked using `require_project_permission(permission)` and `require_project_role(role)`.

### Migration Strategy (Alembic)
- Alembic is configured in `alembic/env.py` to use async engine and dynamically read connection settings from `app.core.config.settings`.
- Models are centralized in `app.core.models` to allow automatic schema detection (`Base.metadata`) and migration generation.

---

## 2. Entity-Relationship Design (Phase 9 Current State)

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : "owns"
    USERS ||--o{ PROJECTS : "owns (as owner)"
    USERS ||--o{ PROJECT_MEMBERS : "has"
    PROJECTS ||--o{ PROJECT_MEMBERS : "contains"
    PROJECTS ||--o{ TASKS : "contains"
    PROJECTS ||--o{ LABELS : "defines"
    USERS ||--o{ TASKS : "creates (creator)"
    USERS ||--o{ TASKS : "assigned (assignee)"
    TASKS ||--o{ COMMENTS : "contains"
    USERS ||--o{ COMMENTS : "writes (author)"
    TASKS }o--o{ LABELS : "tagged via task_labels"
    TASKS ||--o{ ATTACHMENTS : "contains"
    USERS ||--o{ ATTACHMENTS : "uploads"
    PROJECTS ||--o{ ACTIVITY_LOGS : "tracks"
    TASKS ||--o{ ACTIVITY_LOGS : "logs"
    USERS ||--o{ ACTIVITY_LOGS : "performs"
    
    USERS {
        uuid id PK
        string email UK "indexed"
        string password_hash
        string first_name
        string last_name
        string avatar_url
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    REFRESH_TOKENS {
        uuid id PK
        uuid user_id FK "indexed"
        string token_hash UK "indexed"
        datetime expires_at "indexed"
        boolean is_revoked
        datetime created_at
    }

    PROJECTS {
        uuid id PK
        string name "indexed"
        text description
        uuid owner_id FK "indexed"
        boolean is_archived
        datetime created_at
        datetime updated_at
    }

    PROJECT_MEMBERS {
        uuid id PK
        uuid project_id FK "indexed"
        uuid user_id FK "indexed"
        string role "indexed"
        datetime created_at
        datetime updated_at
    }

    TASKS {
        uuid id PK
        uuid project_id FK "indexed"
        string title "indexed"
        text description
        string status "indexed"
        string priority "indexed"
        uuid assignee_id FK "indexed"
        uuid creator_id FK "indexed"
        datetime due_date "indexed"
        float position "indexed"
        json custom_fields
        datetime created_at
        datetime updated_at
    }

    LABELS {
        uuid id PK
        uuid project_id FK "indexed"
        string name "indexed"
        string color
        string description
        datetime created_at
        datetime updated_at
    }

    ATTACHMENTS {
        uuid id PK
        uuid task_id FK "indexed"
        uuid uploader_id FK "indexed"
        string file_name
        string file_path
        bigint file_size
        string content_type
        datetime created_at "indexed"
    }

    COMMENTS {
        uuid id PK
        uuid task_id FK "indexed"
        uuid author_id FK "indexed"
        text content
        datetime created_at "indexed"
        datetime updated_at
    }

    ACTIVITY_LOGS {
        uuid id PK
        uuid project_id FK "indexed"
        uuid task_id FK "indexed, nullable"
        uuid user_id FK "indexed"
        string action "indexed"
        string entity_type "indexed"
        uuid entity_id "indexed"
        json details
        datetime created_at "indexed"
    }
```
