# 🚀 Project Management Platform

## Master Implementation Specification & Agent Prompt

> **IMPORTANT:** This document is the single source of truth for the entire project.
>
> The AI coding agent must follow this document strictly.
>
> The agent must implement the project **phase by phase** and must **STOP after every phase** until the user explicitly confirms continuation.
>
> The user should not need to write code manually.

---

# 1. Project Overview

Build a production-style **Project Management Platform** consisting of

* Python Backend
* Next.js Frontend
* PostgreSQL Database
* Redis
* Background Worker
* Dockerized development environment
* Automated tests
* API documentation
* Authentication and authorization
* Role-Based Access Control
* Caching
* Background jobs
* Clean architecture
* Production-oriented error handling
* Observability/logging
* CI pipeline

The main purpose of the project is to demonstrate strong practical knowledge of:

* Python backend development
* FastAPI
* RESTful API design
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* JWT authentication
* RBAC
* Redis
* Docker
* Docker Compose
* Pytest
* Background jobs
* Microservice-oriented architecture
* Clean architecture
* API security
* Testing
* Debugging
* Deployment concepts

The project must look and behave like a serious backend engineering project rather than a simple CRUD/TODO application. also project be with morden and professional UI and UX. also project be farsi so use vazirmatn and Follow the RTL layout. also use shadcn ui for the frontend. and use typescript for the frontend. The backend folder should be created next to the frontend folder.

---

# 2. Project Concept

The platform allows users to:

1. Create an account.
2. Authenticate securely.
3. Create projects.
4. Invite other users to projects.
5. Assign roles.
6. Create and manage tasks.
7. Assign tasks to team members.
8. Add comments.
9. Track task status.
10. Filter and search tasks.
11. Receive notifications.
12. View project activity.
13. Use pagination.
14. Use cached endpoints.
15. Perform authenticated API operations.
16. Access the system through a modern Next.js frontend.

---

# 3. Core Architecture

Use the following high-level architecture:

```text
                         ┌─────────────────────┐
                         │      Next.js        │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend API    │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
       │ PostgreSQL  │       │    Redis    │      │   Worker    │
       │  Database   │       │ Cache/Queue │      │ Background  │
       └─────────────┘       └─────────────┘      └─────────────┘
```

The initial backend should follow a **modular monolith architecture**.

Do NOT create unnecessary microservices.

The architecture should be designed so that independent modules can later be extracted into separate services.

---

# 4. Technology Stack

## Backend

Mandatory:

* Python 3.12+
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy 2.x
* Alembic
* PostgreSQL
* Redis
* Pytest
* HTTPX
* JWT
* Password hashing
* Docker

Recommended:

* `pydantic-settings`
* `python-multipart`
* `email-validator`
* `passlib` or modern password hashing implementation
* `redis-py`
* `ruff`
* `mypy`

---

## Frontend

Use:

* Next.js
* TypeScript
* Tailwind CSS
* Modern component architecture
* React Query / TanStack Query where appropriate
* Form validation
* Authentication state management

The frontend is secondary to the backend.

Backend quality must always take priority over frontend complexity.

---

## Infrastructure

Use:

* Docker
* Docker Compose
* PostgreSQL
* Redis
* Backend container
* Worker container
* Frontend container

Development should be reproducible using Docker Compose.

Target:

```bash
docker compose up --build
```

should start the complete development environment.

---

# 5. Functional Modules

The backend must contain the following modules.

## Authentication

Features:

* Registration
* Login
* Logout
* Access tokens
* Refresh tokens
* Password hashing
* Password validation
* Current-user endpoint
* Token refresh
* Token expiration
* Secure authentication flow

Endpoints should follow:

```text
/api/v1/auth/register
/api/v1/auth/login
/api/v1/auth/refresh
/api/v1/auth/logout
/api/v1/auth/me
```

---

# 6. Users

Users must have:

* UUID
* Email
* Password hash
* First name
* Last name
* Avatar URL
* Active status
* Created timestamp
* Updated timestamp

Users must never expose password hashes through API responses.

---

# 7. Projects

Users can:

* Create projects
* Update projects
* Delete projects
* View projects
* List projects

Example:

```text
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

Projects should contain:

* ID
* Name
* Description
* Owner
* Status
* Created timestamp
* Updated timestamp

---

# 8. Project Membership

Projects support multiple users.

Roles:

```text
OWNER
ADMIN
MEMBER
VIEWER
```

Permissions must be enforced server-side.

Example:

```text
OWNER
 ├── Manage project
 ├── Manage members
 ├── Manage roles
 └── Delete project

ADMIN
 ├── Manage project
 ├── Manage members
 └── Manage tasks

MEMBER
 ├── View project
 ├── Create tasks
 ├── Update assigned tasks
 └── Comment

VIEWER
 └── Read-only access
```

Never trust frontend permissions.

All authorization must be enforced by the backend.

---

# 9. Tasks

Tasks are the primary business entity.

Each task should support:

* Title
* Description
* Status
* Priority
* Due date
* Assignee
* Creator
* Project
* Created timestamp
* Updated timestamp

Statuses:

```text
TODO
IN_PROGRESS
IN_REVIEW
DONE
CANCELLED
```

Priorities:

```text
LOW
MEDIUM
HIGH
URGENT
```

Endpoints:

```text
POST   /api/v1/projects/{project_id}/tasks
GET    /api/v1/projects/{project_id}/tasks
GET    /api/v1/tasks/{task_id}
PATCH  /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
```

---

# 10. Task Filtering

The API must support:

* Status filtering
* Priority filtering
* Assignee filtering
* Search
* Due-date filtering
* Sorting
* Pagination

Example:

```text
GET /api/v1/projects/{id}/tasks
    ?status=IN_PROGRESS
    &priority=HIGH
    &page=1
    &page_size=20
    &sort=created_at
```

Pagination must be implemented correctly.

Do not load the entire table into memory.

---

# 11. Comments

Users can comment on tasks.

Features:

* Create comment
* List comments
* Edit own comment
* Delete own comment
* Permission checks

Example:

```text
POST   /api/v1/tasks/{task_id}/comments
GET    /api/v1/tasks/{task_id}/comments
PATCH  /api/v1/comments/{comment_id}
DELETE /api/v1/comments/{comment_id}
```

---

# 12. Activity Log

The system should track important events.

Examples:

```text
PROJECT_CREATED
PROJECT_UPDATED
MEMBER_INVITED
MEMBER_ROLE_CHANGED
TASK_CREATED
TASK_ASSIGNED
TASK_STATUS_CHANGED
COMMENT_CREATED
```

Activity logs should contain:

* Actor
* Event type
* Entity
* Entity ID
* Metadata
* Timestamp

This should be designed as an append-only event history.

---

# 13. Notifications

Implement a notification system.

Examples:

* Task assigned to user
* User invited to project
* Task status changed
* Comment added
* Mention created

Notifications should be stored in the database.

Example:

```text
GET  /api/v1/notifications
PATCH /api/v1/notifications/{id}/read
PATCH /api/v1/notifications/read-all
```

---

# 14. Background Jobs

Do not send expensive/non-critical operations directly inside the request lifecycle.

Use Redis-backed background processing.

Examples:

```text
Task assignment
      ↓
Create notification
      ↓
Queue background job
      ↓
Worker processes job
      ↓
Notification delivered
```

The worker should be independently runnable.

The architecture should support future email notifications.

---

# 15. Email Notification

Implement an email abstraction.

Do NOT hard-code a real external email provider.

Create an interface/service such as:

```text
EmailService
```

The implementation should support:

* Development email logging
* Future SMTP/provider integration

Example:

```text
User invited
     ↓
Background Job
     ↓
Email Service
     ↓
Development Logger
```

This allows a real provider to be added later without changing business logic.

---

# 16. Redis

Redis should be used for:

### Caching

Example:

```text
GET /projects/{id}
```

Flow:

```text
Request
   ↓
Redis?
 ┌─┴─┐
Yes No
 │   │
 │   ▼
 │ PostgreSQL
 │   │
 └───┘
   ↓
Response
```

Cache invalidation must be implemented when relevant entities change.

---

# 17. Rate Limiting

Implement basic API rate limiting.

At minimum protect:

```text
/login
/register
/refresh
```

The implementation should prevent trivial brute-force abuse.

Redis may be used for rate-limit state.

---

# 18. Security Requirements

Security is a first-class concern.

Implement:

* Password hashing
* JWT
* Refresh token handling
* Token expiration
* Role-based authorization
* Input validation
* Request validation
* Safe error responses
* CORS configuration
* Environment-based secrets
* No secrets committed to Git
* No password hashes in API responses
* No sensitive data in logs

Never hard-code:

```text
JWT_SECRET
DATABASE_URL
REDIS_URL
```

Use environment variables.

---

# 19. Database Design

Use PostgreSQL.

Use SQLAlchemy 2.x.

Use Alembic for migrations.

Suggested entities:

```text
User
Project
ProjectMember
Task
Comment
Notification
ActivityLog
RefreshToken
```

Relationships must be properly modeled.

Use:

* Foreign keys
* Indexes
* Unique constraints
* Appropriate cascade behavior
* Timestamps

Important indexes should be added based on actual query patterns.

---

# 20. ORM Requirements

The project must demonstrate proper ORM usage.

The agent must avoid:

* N+1 queries
* unnecessary queries
* loading huge collections
* inefficient relationships

The implementation should use appropriate:

* eager loading
* select statements
* joins
* pagination
* transactions

The README should eventually explain the important ORM decisions.

---

# 21. Backend Architecture

Use a clean modular structure.

Recommended structure:

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── projects/
│   │   ├── tasks/
│   │   ├── comments/
│   │   ├── notifications/
│   │   └── activity/
│   │
│   ├── services/
│   ├── repositories/
│   ├── workers/
│   └── shared/
│
├── tests/
├── alembic/
├── Dockerfile
├── pyproject.toml
└── .env.example
```

The exact structure may be improved by the agent if there is a strong architectural reason.

Do not create unnecessary abstraction layers.

---

# 22. API Versioning

All APIs must be versioned:

```text
/api/v1/...
```

The API must have consistent:

* URL naming
* HTTP methods
* status codes
* error responses
* response schemas
* pagination format

---

# 23. Error Handling

Create centralized error handling.

Errors should have predictable structure.

Example:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project was not found",
    "details": null
  }
}
```

Never expose internal stack traces to clients in production mode.

---

# 24. Logging

Implement structured application logging.

Log:

* Request lifecycle
* Important business events
* Errors
* Background job failures

Never log:

* Passwords
* JWT secrets
* Refresh tokens
* Sensitive user data

---

# 25. Testing

Testing is mandatory.

Use Pytest.

Minimum categories:

```text
tests/
├── unit/
├── integration/
└── api/
```

Test:

### Authentication

* registration
* login
* invalid password
* expired token
* refresh token
* unauthorized access

### Authorization

* owner permissions
* admin permissions
* member permissions
* viewer permissions

### Projects

* create
* update
* delete
* access control

### Tasks

* CRUD
* assignment
* filtering
* pagination
* permissions

### Comments

* CRUD
* ownership

### Notifications

* creation
* read/unread state

---

# 26. Test Quality

Do not create fake tests that simply make coverage numbers look good.

Tests should verify actual behavior.

The agent should fix implementation problems discovered by tests rather than weakening tests.

Target a strong meaningful coverage level.

---

# 27. API Documentation

FastAPI's OpenAPI documentation must be clean.

All important endpoints should contain:

* Summary
* Description
* Request schema
* Response schema
* Status codes
* Authentication requirements

The API should be testable through:

```text
/docs
/redoc
```

---

# 28. Frontend

Create a modern Next.js frontend.

The frontend must include:

### Authentication

* Login
* Register
* Logout

### Dashboard

* Project overview
* Recent tasks
* Notifications

### Projects

* Project list
* Project details
* Members

### Tasks

* Task list
* Create task
* Edit task
* Task details
* Filters
* Search
* Pagination

### Notifications

* Notification list
* Read/unread state

The frontend must consume the real backend.

Do not mock the backend in the final version.

---

# 29. Frontend Design

The UI should be clean and professional.

Prioritize:

* usability
* responsive design
* loading states
* empty states
* error states
* form validation
* accessibility

Do not spend excessive development time on visual effects.

The primary purpose of the project is backend engineering.


## UI/UX Design Direction — Premium Modern Product Experience

The frontend must have a **premium, modern, polished SaaS-product-quality UI/UX**, comparable in overall quality and attention to detail to modern products such as Linear, Vercel, Notion, Raycast, and other high-quality developer-focused SaaS applications. Do NOT create a generic admin dashboard, template-like interface, or basic CRUD UI. The interface should feel like a real commercial product that could be shown directly in a professional portfolio. Prioritize a strong visual hierarchy, excellent typography, generous and consistent spacing, carefully designed cards and surfaces, subtle borders, elegant shadows, sophisticated use of color, beautiful empty states, polished forms, responsive layouts, and consistent component design. Use a cohesive design system across the entire application rather than styling each page independently. The application should support both light and dark themes if practical, with the dark theme receiving special attention because it should feel premium rather than simply being a black background. Use tasteful gradients, subtle glass/blur effects, layered surfaces, soft highlights, and accent colors only where they improve hierarchy and visual identity; avoid excessive gradients, excessive glassmorphism, neon effects, or visual noise. The application should include **high-quality micro-interactions and purposeful animations throughout the experience**: smooth page and route transitions, animated sidebar/navigation states, hover and focus states, button feedback, modal/dialog transitions, dropdown animations, toast notifications, skeleton loading animations, list/item entrance animations, task status transitions, drag-and-drop feedback where appropriate, notification animations, and subtle dashboard metric animations. Animations must feel intentional, fast, smooth, and professional rather than decorative; never sacrifice usability or performance for animation. Prefer modern animation tooling such as Framer Motion/Motion where appropriate, but do not overuse animation. Every interactive element must have clear hover, active, focus, disabled, loading, success, and error states where applicable. Forms must feel polished and provide excellent validation feedback. Loading states should use skeletons rather than abrupt blank screens whenever appropriate, and every major page must have thoughtful loading, empty, error, and success states. Tables, lists, task boards, dialogs, dropdowns, filters, search interfaces, pagination, notification panels, and dashboards should all feel carefully designed rather than generated from default component-library styles. The task management experience should be particularly polished, with a visually clear task hierarchy, status indicators, priority indicators, assignee avatars, due dates, filtering controls, and smooth interactions. The dashboard should communicate useful information immediately through well-designed cards, activity feeds, task summaries, project progress indicators, and notification surfaces without becoming visually cluttered. Responsive behavior is mandatory: the application must work beautifully on desktop, tablet, and mobile sizes, with layouts intentionally adapted for smaller screens rather than simply shrinking desktop layouts. Accessibility must be treated as part of the design: use semantic HTML, keyboard navigation, visible focus states, appropriate ARIA attributes, sufficient contrast, reduced-motion support, and accessible form controls. Use a professional icon system such as Lucide rather than arbitrary Unicode symbols or emoji. Avoid unnecessary decorative elements, excessive rounded cards, giant typography, excessive shadows, inconsistent border radii, inconsistent spacing, and generic Tailwind-looking interfaces. Do not introduce a new visual pattern on every page; establish reusable design tokens and components for typography, colors, spacing, radius, shadows, buttons, inputs, cards, dialogs, badges, avatars, tooltips, dropdowns, tabs, navigation, notifications, and data visualization, and reuse them consistently. Before implementing individual pages, establish the application's visual language and component foundation first. The final result should feel cohesive, intentional, highly polished, technically sophisticated, and visually memorable while remaining practical and usable. **The goal is not to make the UI flashy; the goal is to make it feel expensive, refined, modern, responsive, and production-ready.**



---

# 30. Docker

Create:

```text
docker-compose.yml
```

Services:

```text
frontend
backend
postgres
redis
worker
```

Development should work with:

```bash
docker compose up --build
```

The agent must ensure:

* services communicate correctly
* environment variables work
* migrations can run
* database persists
* Redis works
* worker starts correctly

---

# 31. Environment Variables

Provide:

```text
.env.example
```

Example categories:

```text
DATABASE_URL=
REDIS_URL=
JWT_SECRET=
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=
JWT_REFRESH_TOKEN_EXPIRE_DAYS=
CORS_ORIGINS=
ENVIRONMENT=
```

Never commit `.env`.

---

# 32. Code Quality

Use:

* Ruff
* formatting
* type hints
* meaningful names
* small functions
* clear modules

Avoid:

* giant files
* giant functions
* duplicated business logic
* unnecessary abstractions
* magic values
* commented-out dead code

---

# 33. Git Strategy

Use meaningful commits.

Examples:

```text
feat(auth): implement JWT authentication
feat(projects): add project management
feat(tasks): implement task lifecycle
feat(redis): add project caching
feat(worker): add notification jobs
test(auth): add authentication integration tests
fix(tasks): prevent unauthorized task updates
docs: improve local development guide
```

Do not create meaningless commits such as:

```text
update
fix
test
changes
final
final2
```

---

# 34. CI

Create a GitHub Actions workflow.

At minimum:

```text
Install dependencies
       ↓
Lint
       ↓
Type check
       ↓
Run tests
       ↓
Build
```

The pipeline must fail when tests or linting fail.

---

# 35. Health Checks

Implement:

```text
GET /health
GET /health/ready
```

The readiness endpoint should verify important dependencies.

Example:

```text
API
 ├── PostgreSQL ✓
 └── Redis ✓
```

---

# 36. Project Documentation

The repository must contain:

```text
README.md
ARCHITECTURE.md
API.md
CONTRIBUTING.md
.env.example
```

README must include:

* Project overview
* Architecture
* Features
* Tech stack
* Requirements
* Installation
* Docker setup
* Environment variables
* Database migrations
* Running tests
* API documentation
* Project structure
* Architecture decisions
* Troubleshooting
* Future improvements

---

# 37. Architecture Documentation

`ARCHITECTURE.md` should explain:

* Why FastAPI
* Why PostgreSQL
* Why SQLAlchemy
* Why Redis
* Why background workers
* Why modular monolith
* Authentication architecture
* Authorization architecture
* Caching strategy
* Database design
* Error handling
* Testing strategy

This documentation is important for technical interviews.

---

# 38. API Design Principles

Follow REST principles.

Use proper HTTP methods:

```text
GET
POST
PATCH
DELETE
```

Use meaningful HTTP status codes:

```text
200
201
204
400
401
403
404
409
422
429
500
```

Do not return `200 OK` for every situation.

---

# 39. Performance

Implement reasonable backend optimizations.

Examples:

* pagination
* database indexes
* Redis caching
* efficient SQL queries
* eager loading where necessary
* avoiding N+1
* background processing

Do not optimize blindly.

Document meaningful performance decisions.

---

# 40. Observability

Add enough information to debug the application.

At minimum:

* structured logs
* request IDs if practical
* worker job logs
* database error logs
* startup/shutdown logs

---

# 41. Development Workflow

The agent must work according to the following process.

For every phase:

```text
1. Read the entire project specification.
2. Inspect the existing repository.
3. Understand the current architecture.
4. Implement the phase.
5. Run relevant tests.
6. Run linting/type checking.
7. Fix discovered issues.
8. Verify the application.
9. Update documentation.
10. Summarize exactly what changed.
11. STOP.
12. Wait for user approval.
```

The agent must NOT automatically continue to the next phase.

---

# 42. Phase Plan

## Phase 0 — Project Planning

Deliver:

* final architecture
* directory structure
* database ERD
* API module plan
* development roadmap
* Docker architecture
* testing strategy

Do not implement major application features yet.

STOP and ask for confirmation.

---

# Phase 1 — Repository & Infrastructure

Implement:

* repository structure
* Python environment
* FastAPI bootstrap
* Docker
* Docker Compose
* PostgreSQL
* Redis
* environment configuration
* health check

Verify:

```bash
docker compose up --build
```

STOP.

---

# Phase 2 — Database Foundation

Implement:

* SQLAlchemy setup
* Alembic
* database base configuration
* User model
* initial migrations
* database indexes/constraints

Run migrations successfully.

STOP.

---

# Phase 3 — Authentication

Implement:

* registration
* password hashing
* login
* JWT access token
* refresh token
* logout
* current user
* authentication dependencies

Add tests.

STOP.

---

# Phase 4 — Users & RBAC

Implement:

* user profile
* roles
* permissions
* authorization dependencies
* project membership model

Add permission tests.

STOP.

---

# Phase 5 — Projects

Implement:

* project CRUD
* membership
* invitation mechanism
* role management
* project permissions

Add tests.

STOP.

---

# Phase 6 — Tasks

Implement:

* task CRUD
* task assignment
* status
* priority
* due dates
* filtering
* sorting
* search
* pagination

Add tests.

STOP.

---

# Phase 7 — Comments & Activity

Implement:

* comments
* comment permissions
* activity log
* automatic activity events

Add tests.

STOP.

---

# Phase 8 — Redis

Implement:

* Redis integration
* project caching
* cache invalidation
* rate limiting

Add tests where appropriate.

STOP.

---

# Phase 9 — Background Worker

Implement:

* job abstraction
* Redis-backed queue
* worker
* notification jobs
* retry strategy
* failure handling

STOP.

---

# Phase 10 — Notifications & Email

Implement:

* notification model
* notification endpoints
* unread/read state
* email service abstraction
* development email implementation
* background email jobs

STOP.

---

# Phase 11 — Security Hardening

Review and improve:

* authentication
* authorization
* CORS
* rate limiting
* secrets
* input validation
* error handling
* sensitive logging
* token handling

Perform a security review.

STOP.

---

# Phase 12 — Testing & Quality

Implement/finalize:

* unit tests
* integration tests
* API tests
* authentication tests
* authorization tests
* worker tests
* edge cases

Run the full test suite.

STOP.

---

# Phase 13 — Frontend

Implement:

* Next.js application
* authentication
* dashboard
* projects
* tasks
* comments
* notifications
* loading states
* error states
* responsive UI

Connect everything to the real API.

STOP.

---

# Phase 14 — CI/CD

Implement:

* GitHub Actions
* lint
* type checking
* backend tests
* frontend checks
* Docker build verification

STOP.

---

# Phase 15 — Documentation

Finalize:

* README
* architecture documentation
* API documentation
* setup instructions
* troubleshooting
* environment variables
* diagrams
* development workflow

STOP.

---

# Phase 16 — Production Readiness Review

Perform a complete review.

Check:

* architecture
* security
* performance
* database
* API consistency
* testing
* Docker
* logging
* documentation
* frontend/backend integration

Fix all discovered issues.

STOP.

---

# Phase 17 — Portfolio & Resume Preparation

Generate:

1. Final project description.
2. Resume-ready project bullets.
3. Technical interview talking points.
4. Architecture explanation.
5. Backend technologies list.
6. Challenges and solutions.
7. GitHub repository presentation checklist.

Do not invent achievements or metrics.

Only mention things actually implemented.

STOP.

---

# 43. Agent Rules

The coding agent MUST follow these rules.

## Rule 1 — Do not ask unnecessary questions

If a reasonable engineering decision can be made independently, make it.

Only ask the user when:

* a decision fundamentally changes the product
* credentials are required
* external services require user configuration
* there are multiple incompatible architectural choices

Otherwise choose the most professional option.

---

## Rule 2 — Never fake implementation

Do not claim a feature is complete unless:

* code exists
* tests pass where applicable
* integration works
* documentation is updated

---

## Rule 3 — Never skip validation

After implementation:

```text
lint
type check
tests
build
```

must be run where applicable.

---

## Rule 4 — Fix problems before stopping

If tests fail because of your implementation:

1. investigate
2. fix
3. rerun tests
4. only then stop

Do not leave obvious broken functionality for the next phase.

---

## Rule 5 — Preserve working functionality

When implementing a new feature:

* do not unnecessarily rewrite existing modules
* do not break previous APIs
* update tests when behavior intentionally changes

---

## Rule 6 — Keep architecture understandable

Do not over-engineer.

The project should demonstrate engineering maturity, not architectural complexity for its own sake.

---

## Rule 7 — Backend comes first

If time or complexity becomes a problem:

```text
Backend quality
    >
Tests
    >
Architecture
    >
Documentation
    >
Frontend polish
```

Never sacrifice backend quality for visual frontend features.

---

# 44. Definition of Done

The project is considered complete only when:

### Backend

* [ ] FastAPI application works
* [ ] PostgreSQL works
* [ ] SQLAlchemy works
* [ ] Alembic migrations work
* [ ] Redis works
* [ ] Authentication works
* [ ] JWT works
* [ ] RBAC works
* [ ] Projects work
* [ ] Tasks work
* [ ] Comments work
* [ ] Activity logs work
* [ ] Notifications work
* [ ] Background jobs work
* [ ] Rate limiting works
* [ ] Validation works
* [ ] Error handling works
* [ ] Health checks work

### Testing

* [ ] Unit tests
* [ ] Integration tests
* [ ] API tests
* [ ] Authentication tests
* [ ] Authorization tests
* [ ] Worker tests

### Infrastructure

* [ ] Docker
* [ ] Docker Compose
* [ ] PostgreSQL container
* [ ] Redis container
* [ ] Worker container
* [ ] Backend container
* [ ] Frontend container

### Frontend

* [ ] Authentication
* [ ] Dashboard
* [ ] Projects
* [ ] Tasks
* [ ] Comments
* [ ] Notifications
* [ ] Error states
* [ ] Loading states
* [ ] Responsive UI

### Quality

* [ ] Lint passes
* [ ] Type checking passes
* [ ] Tests pass
* [ ] Docker build passes
* [ ] CI passes
* [ ] Documentation complete

---

# 45. Final Agent Instruction

You are the lead software engineer responsible for implementing this project.

Treat this document as the project specification.

Do not simplify the project into a TODO application.

Do not skip backend architecture.

Do not generate fake features.

Do not use mock data in the final implementation.

Do not automatically continue between phases.

At the end of every phase:

1. Explain what was implemented.
2. List important files changed.
3. Report tests/checks executed.
4. Report any known limitations.
5. Confirm the phase is complete.
6. STOP and wait for the user to say something equivalent to:

```text
Continue
```

Only after explicit confirmation may you begin the next phase.

The final result must be a complete, professional, production-style portfolio project demonstrating practical Python backend engineering skills.

The project should be strong enough that a backend interviewer can inspect the repository and discuss:

* Python
* FastAPI
* REST
* PostgreSQL
* SQLAlchemy
* ORM
* JWT
* RBAC
* Redis
* caching
* background jobs
* Docker
* testing
* architecture
* security
* performance
* debugging
* CI/CD
* microservice-oriented design

without the project feeling artificially over-engineered.

**Start with Phase 0 only.**

Do not implement Phase 1 until the user explicitly approves Phase 0.

