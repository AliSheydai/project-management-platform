# Project Management Platform

A full-stack, production-grade Project Management Platform inspired by tools like Linear, Trello, and Jira. Built with a modular monolith architecture, real-time collaboration via WebSockets, role-based access control, and a modern React frontend.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)

---

## Overview

This platform enables teams to manage projects, tasks, and collaboration in real time. It supports:

- Multi-project workspaces with role-based member management
- Kanban board with drag-and-drop task reordering
- Real-time presence and event broadcasting via WebSockets
- Background job processing for emails, cleanup, and analytics
- A responsive, RTL-aware frontend with dark mode support

---

## Architecture

The system follows a **modular monolith** design. Backend modules are encapsulated with explicit models, schemas, services, and API routers. This ensures high development velocity while maintaining clean domain boundaries for future microservice extraction.

```
                         ┌─────────────────────┐
                         │      Next.js        │
                         │   React 19 Frontend │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST + WebSocket
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │   Backend API       │
                         └──────────┬──────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
        ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
        │ PostgreSQL  │      │    Redis    │     │  ARQ Worker │
        │  Database   │      │ Cache/PubSub│     │ Background  │
        └─────────────┘      └─────────────┘     └─────────────┘
```

### Key Architectural Decisions

- **Asynchronous I/O**: Full async stack with SQLAlchemy 2.0 `AsyncEngine` + `asyncpg` for non-blocking database access
- **RBAC**: Granular permission matrix with 4 roles (OWNER, ADMIN, MEMBER, VIEWER) and 14 distinct permissions
- **Real-Time**: WebSocket `ConnectionManager` with project rooms, presence tracking, and Redis Pub/Sub for multi-worker broadcast
- **Background Jobs**: ARQ task queue with Redis backend for email sending, session cleanup, and activity aggregation
- **Rate Limiting**: SlowAPI with Redis-backed storage and automatic in-memory fallback
- **Security Headers**: CSP, HSTS, X-Frame-Options, and more injected via custom middleware

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3.12** | Runtime |
| **FastAPI** | Async web framework with automatic OpenAPI docs |
| **SQLAlchemy 2.0** | Async ORM with declarative mapped columns |
| **asyncpg** | High-performance async PostgreSQL driver |
| **Alembic** | Database migration management |
| **PostgreSQL 16** | Primary relational database |
| **Redis 7** | Caching, Pub/Sub, rate limit storage, job queue |
| **ARQ** | Async background job worker with retry policies |
| **PyJWT** | JWT token generation and verification |
| **Passlib + bcrypt** | Password hashing |
| **SlowAPI** | Rate limiting middleware |
| **Pydantic v2** | Data validation and settings management |
| **Uvicorn** | ASGI server |
| **Docker** | Containerization |

### Frontend

| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework with App Router |
| **React 19** | UI library |
| **TypeScript** | Type-safe development |
| **Tailwind CSS 4** | Utility-first styling |
| **shadcn/ui** | Accessible component library (61 UI components) |
| **TanStack React Query** | Server state management and caching |
| **Zustand** | Client-side state management (auth store) |
| **Axios** | HTTP client with automatic token refresh |
| **Zod** | Schema validation |
| **React Hook Form** | Form management |
| **Recharts** | Dashboard charts and analytics |
| **Motion (Framer Motion)** | Animations |
| **date-fns + date-fns-jalali** | Date formatting (Gregorian + Jalali/Shamsi) |
| **Lucide React** | Icon library |
| **Sonner** | Toast notifications |
| **Vitest** | Unit testing |

### DevOps & Infrastructure

| Technology | Purpose |
|---|---|
| **Docker Compose** | Multi-service local development |
| **Multi-stage Dockerfiles** | Optimized production images |
| **Vercel** | Frontend deployment (configured) |
| **Ruff** | Python linting and formatting |
| **ESLint** | TypeScript/React linting |

---

## Features

### Authentication & Sessions
- User registration with email/password
- JWT-based authentication with access + refresh token pair
- Token rotation (refresh token invalidated on each use)
- Automatic token refresh on the client with request queuing
- Session storage in `sessionStorage` (XSS-safe vs localStorage)
- Server-side session cleanup via background worker

### Projects & Workspaces
- Create, update, archive, and delete projects
- Invite members by email with role assignment
- Role management (OWNER, ADMIN, MEMBER, VIEWER)
- Member removal and self-leave functionality
- Project overview with statistics

### Tasks & Kanban
- Create, update, delete tasks with title, description, status, priority, assignee, due date
- Kanban board with 5 columns: BACKLOG, TODO, IN_PROGRESS, IN_REVIEW, DONE
- Drag-and-drop task reordering with optimistic updates
- Task detail sheet with full editing capabilities
- Task filtering by status, priority, assignee, and search query
- Task sorting by multiple fields

### Labels & Metadata
- Create colored labels per project
- Attach/detach labels to tasks
- Label-based filtering in search

### Comments & Collaboration
- Add, edit, delete comments on tasks
- Comment authorship tracking
- Activity feed per project and per task

### File Attachments
- Upload files up to 25MB per task
- Support for images, PDFs, text, zip, docx, JSON
- Download and delete attachments
- Storage abstraction layer

### Search & Saved Views
- Cross-project task search with full-text query
- Multi-filter support (status, priority, assignee, date ranges)
- Faceted search results with count breakdowns
- Save and manage custom filter views

### Notifications
- In-app notification system
- Notification types: task assigned, status changed, comment added, user mentioned, project invited
- Unread count badge
- Mark single/all as read
- Real-time delivery via WebSocket

### Real-Time & Presence
- WebSocket connections per project room
- Live presence: who is online in each project
- Real-time event broadcasting: task created/updated/moved/deleted, comment added
- Heartbeat ping/pong for connection health
- Redis Pub/Sub for multi-worker synchronization

### Dashboard
- Project overview with task distribution charts
- Activity statistics
- Quick access to recent projects

### Settings & Profile
- Update user profile (name, avatar, password)
- Appearance settings (theme switching)
- Dark mode support

### Internationalization
- RTL (Right-to-Left) layout support for Persian/Farsi
- Jalali (Shamsi) calendar integration
- Persian number formatting
- Localized toast messages

---

## Project Structure

```
project-management/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/                   # API route handlers
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── users.py              # User profile endpoints
│   │   │   ├── projects.py           # Project CRUD + members
│   │   │   ├── tasks.py              # Task CRUD + reorder
│   │   │   ├── comments.py           # Comment endpoints
│   │   │   ├── labels.py             # Label management
│   │   │   ├── attachments.py        # File upload/download
│   │   │   ├── search.py             # Global search + saved views
│   │   │   ├── notifications.py      # Notification endpoints
│   │   │   ├── activity.py           # Activity log endpoints
│   │   │   ├── websockets.py         # WebSocket connection endpoint
│   │   │   ├── health.py             # Health check endpoints
│   │   │   └── router.py             # Central API router
│   │   ├── core/                     # Shared infrastructure
│   │   │   ├── config.py             # Pydantic settings
│   │   │   ├── database.py           # Async SQLAlchemy engine
│   │   │   ├── security.py           # JWT + password utilities
│   │   │   ├── permissions.py        # RBAC roles & permission matrix
│   │   │   ├── dependencies.py       # FastAPI dependency factories
│   │   │   ├── websockets.py         # ConnectionManager + presence
│   │   │   ├── redis.py              # Redis connection pool
│   │   │   ├── queue.py              # ARQ job queue client
│   │   │   ├── rate_limit.py         # SlowAPI rate limiter
│   │   │   ├── middleware.py         # Security headers middleware
│   │   │   ├── exceptions.py         # Global exception handlers
│   │   │   ├── logging.py            # Structured logging setup
│   │   │   └── models.py             # Base model imports
│   │   ├── modules/                  # Domain modules
│   │   │   ├── auth/                 # Auth models, schemas, service
│   │   │   ├── users/                # User models, schemas, service
│   │   │   ├── projects/             # Project + member management
│   │   │   ├── tasks/                # Task models, schemas, service
│   │   │   ├── comments/             # Comment models, schemas, service
│   │   │   ├── labels/               # Label models, schemas, service
│   │   │   ├── attachments/          # Attachment + storage service
│   │   │   ├── search/               # Search + saved views
│   │   │   ├── notifications/        # Notification models + service
│   │   │   └── activity/             # Activity log models + service
│   │   ├── shared/
│   │   │   └── models.py             # UUIDMixin, TimestampMixin
│   │   ├── workers/
│   │   │   ├── runner.py             # ARQ worker entry point
│   │   │   └── email.py              # Email rendering + sending
│   │   └── main.py                   # FastAPI application factory
│   ├── alembic/                      # Database migrations
│   │   ├── env.py                    # Async migration environment
│   │   └── versions/                 # Migration scripts
│   ├── tests/
│   │   ├── api/                      # API endpoint tests (15 files)
│   │   ├── unit/                     # Unit tests (7 files)
│   │   └── integration/              # Integration tests
│   ├── uploads/                      # File upload storage
│   ├── pyproject.toml                # Python project config
│   ├── requirements.txt              # Pinned dependencies
│   ├── Dockerfile                    # Backend container
│   └── Dockerfile.worker             # Worker container
│
├── frontend/                         # Next.js React frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── (auth)/               # Auth route group
│   │   │   │   ├── login/            # Login page
│   │   │   │   └── register/         # Register page
│   │   │   ├── (app)/                # Protected route group
│   │   │   │   ├── dashboard/        # Dashboard page
│   │   │   │   ├── projects/         # Projects list + detail
│   │   │   │   │   └── [projectId]/  # Dynamic project routes
│   │   │   │   │       ├── overview/ # Project overview
│   │   │   │   │       ├── tasks/    # Kanban board
│   │   │   │   │       ├── members/  # Member management
│   │   │   │   │       └── activity/ # Activity feed
│   │   │   │   ├── notifications/    # Notifications page
│   │   │   │   └── settings/         # User settings
│   │   │   ├── layout.tsx            # Root layout
│   │   │   └── globals.css           # Global styles
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # 61 shadcn/ui components
│   │   │   ├── layout/               # AppShell, Sidebar, TopBar
│   │   │   ├── auth/                 # LoginForm, RegisterForm
│   │   │   ├── tasks/                # KanbanBoard, TaskDetailSheet
│   │   │   ├── projects/             # ProjectList, ProjectOverview
│   │   │   ├── dashboard/            # DashboardView
│   │   │   ├── members/              # MembersView
│   │   │   ├── activity/             # ActivityView
│   │   │   ├── notifications/        # NotificationsView
│   │   │   ├── settings/             # ProfileForm, AppearanceForm
│   │   │   └── shared/               # Reusable components
│   │   ├── features/                 # Feature-specific hooks
│   │   │   ├── tasks/hooks.ts        # Task React Query hooks
│   │   │   ├── projects/hooks.ts     # Project React Query hooks
│   │   │   ├── comments/             # Comment hooks
│   │   │   ├── notifications/        # Notification hooks
│   │   │   └── users/                # User hooks
│   │   ├── lib/                      # Utilities and services
│   │   │   ├── api/                  # API client modules (14 files)
│   │   │   ├── auth/                 # Token store + Zustand session
│   │   │   ├── supabase/             # Supabase SSR client
│   │   │   ├── validations/          # Zod schemas
│   │   │   ├── constants/            # App constants
│   │   │   ├── dates/                # Date utilities
│   │   │   ├── permissions.ts        # Client-side RBAC helpers
│   │   │   ├── query-keys.ts         # React Query key factory
│   │   │   └── utils.ts              # General utilities
│   │   ├── providers/                # React context providers
│   │   │   ├── auth-provider.tsx     # Auth state restoration
│   │   │   ├── query-provider.tsx    # React Query provider
│   │   │   └── theme-provider.tsx    # Theme provider
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── types/                    # TypeScript type definitions
│   │   ├── config/                   # App configuration
│   │   └── middleware.ts             # Next.js middleware
│   ├── public/                       # Static assets
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── next.config.ts                # Next.js config
│   ├── vitest.config.ts              # Test config
│   ├── Dockerfile                    # Production container
│   ├── Dockerfile.dev                # Development container
│   └── vercel.json                   # Vercel deployment config
│
├── docker-compose.yml                # Multi-service orchestration
├── .env.example                      # Environment variables template
├── API.md                            # Full API documentation
├── ARCHITECTURE.md                   # Architecture deep-dive
└── README.md                         # This file
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (recommended)
- PostgreSQL 16 (if running without Docker)
- Redis 7 (if running without Docker)

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd project-management

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# The application is now running:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env with your database and Redis credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ENVIRONMENT` | App environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing secret | (dev default) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL for frontend | `ws://localhost:8000/api/v1/ws` |

---

## API Reference

All endpoints are versioned under `/api/v1`. Full documentation is available at `http://localhost:8000/docs` (Swagger UI) and in [API.md](./API.md).

### Endpoint Summary

| Module | Endpoints | Description |
|---|---|---|
| **Auth** | `POST /auth/register`, `/login`, `/refresh`, `/logout`, `GET /auth/me` | Authentication & session management |
| **Users** | `GET/PATCH /users/me`, `GET /users/{id}`, `GET /users` | User profiles & directory |
| **Projects** | `POST/GET/PATCH/DELETE /projects`, member management | Project CRUD & membership |
| **Tasks** | `POST/GET/PATCH/DELETE /tasks`, `PATCH /tasks/{id}/reorder` | Task management & Kanban |
| **Comments** | `POST/GET/PATCH/DELETE /comments` | Task comments |
| **Labels** | `POST/GET/PATCH/DELETE /labels`, attach/detach | Task labeling system |
| **Attachments** | `POST/GET/DELETE /attachments`, download | File upload & management |
| **Search** | `GET /search/tasks`, saved views CRUD | Global search & filters |
| **Notifications** | `GET/PATCH/DELETE /notifications`, unread count | In-app notifications |
| **Activity** | `GET /projects/{id}/activity`, `/tasks/{id}/activity` | Audit trail |
| **WebSocket** | `WS /ws/projects/{id}` | Real-time events & presence |
| **Health** | `GET /health`, `/health/ready` | Service health checks |

### RBAC Permission Matrix

| Permission | OWNER | ADMIN | MEMBER | VIEWER |
|---|---|---|---|---|
| Project view | Yes | Yes | Yes | Yes |
| Project edit/delete | Yes | Yes | - | - |
| Member invite/remove | Yes | Yes | - | - |
| Role change | Yes | - | - | - |
| Task create/edit/delete | Yes | Yes | Create/Edit own | - |
| Comment create | Yes | Yes | Yes | - |
| Comment delete | Yes | Yes | Own only | - |

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/api/          # API endpoint tests
pytest tests/unit/         # Unit tests
pytest tests/integration/  # Integration tests
```

**Test Coverage:**
- 15 API test files covering all endpoints
- 7 unit test files for config, database, models, permissions, RBAC, security, workers
- Integration tests for database model behavior
- Rate limiting and security header tests
- WebSocket connection tests

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run in watch mode
npm run test:watch
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check .
ruff format --check .

# Frontend linting
cd frontend
npm run lint
```

---

## Deployment

### Docker Production Build

```bash
# Build and start production containers
docker-compose -f docker-compose.yml up -d --build
```

### Vercel (Frontend)

The frontend is configured for Vercel deployment with:
- `vercel.json` configuration
- `NEXT_PUBLIC_API_URL` environment variable (required)
- Standalone output for Docker, native output for Vercel

### Production Checklist

- Change `JWT_SECRET` to a strong random value
- Set `ENVIRONMENT=production`
- Configure proper `CORS_ORIGINS`
- Set up SSL/TLS termination
- Configure PostgreSQL with connection pooling
- Set up Redis persistence
- Configure file upload storage (S3 or equivalent)
- Set up monitoring and logging aggregation

---

## Security

- **JWT Authentication**: Short-lived access tokens (30 min) with rotating refresh tokens (7 days)
- **Password Hashing**: bcrypt via Passlib
- **RBAC**: 4-tier role hierarchy with granular permission checks on every endpoint
- **Rate Limiting**: Per-endpoint throttling (login: 5/min, register: 10/hour, attachments: 15/min)
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- **CORS**: Configurable allowed origins with credential support
- **Input Validation**: Pydantic v2 schemas on all inputs
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **File Upload Validation**: Content-type checking, size limits (25MB)
- **WebSocket Authentication**: JWT verification on connection upgrade

---

## License

This project is for educational and portfolio purposes.
