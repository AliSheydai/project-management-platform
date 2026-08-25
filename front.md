# 🚀 Project Management Platform

# Frontend Master Implementation Specification

> **ROLE:** You are the Lead Frontend Engineer, Product Designer, UX Engineer, and Frontend Architect responsible for implementing the complete frontend of this project.
>
> This document is the **single source of truth for the frontend implementation**.
>
> The backend already exists or is being implemented separately according to the project's backend specification.
>
> Your responsibility is to build a **complete, production-quality Next.js frontend** that connects to the real backend API and provides a polished, modern, responsive, accessible, and highly interactive product experience.
>
> The user should not need to manually write frontend code.
>
> Implement the frontend **phase by phase**.
>
> **STOP after every phase and wait for explicit user approval before continuing.**
>
> Do not automatically proceed to the next phase.

---

# 1. PRIMARY OBJECTIVE

Build a complete SaaS-quality frontend for the Project Management Platform.

The frontend must NOT look like:

* a generic admin dashboard
* a Tailwind starter template
* a CRUD demo
* a simple TODO application
* a collection of disconnected pages
* a UI built only to satisfy functional requirements

It must feel like a **real commercial SaaS product**.

The final experience should be:

* modern
* premium
* elegant
* fast
* responsive
* accessible
* intuitive
* visually coherent
* highly interactive
* production-ready

The quality target should be comparable in design philosophy and polish to products such as:

* Linear
* Vercel
* Notion
* Raycast
* modern productivity SaaS applications

Do NOT copy their interfaces.

Use them only as inspiration for:

* information hierarchy
* interaction quality
* spacing
* typography
* motion
* visual polish
* product thinking

---

# 2. NON-NEGOTIABLE REQUIREMENT

The frontend MUST connect to the **real backend API**.

Do NOT use fake/mock data in the final implementation.

Do NOT hard-code project lists.

Do NOT hard-code tasks.

Do NOT create fake authentication.

Do NOT simulate API responses.

Every production-facing feature must use the real backend.

If the backend endpoint is not implemented yet:

1. inspect the backend code/API documentation
2. determine the intended contract
3. create the frontend integration layer according to the real contract
4. if necessary, temporarily isolate unavailable functionality behind a clearly documented adapter
5. never hide backend integration problems with fake production data

The final application must work end-to-end.

---

# 3. LANGUAGE AND LOCALIZATION

The entire application must be **Persian / Farsi-first**.

Use:

* Persian UI copy
* Persian labels
* Persian validation messages
* Persian empty states
* Persian error messages where appropriate
* Persian date presentation
* Persian-friendly typography

The application must use:

**Vazirmatn**

as the primary font.

Configure it properly using the Next.js font system where appropriate.

The application must use:

# RTL

Right-to-left layout must be treated as a first-class design requirement.

Do NOT simply add:

```html
dir="rtl"
```

and assume the job is complete.

Every component must be reviewed for RTL correctness:

* sidebar
* navigation
* forms
* tables
* dialogs
* dropdowns
* breadcrumbs
* pagination
* task cards
* kanban board
* charts
* notifications
* tooltips
* icons
* directional animations
* spacing
* alignment

Directional icons must also make sense in RTL.

---

# 4. TECHNOLOGY STACK

Use:

## Core

* Next.js
* TypeScript
* React
* App Router

## UI

* Tailwind CSS
* shadcn/ui
* Radix primitives through shadcn/ui
* Lucide icons

## Animation

Use:

* Motion / Framer Motion where appropriate

Animations must be purposeful and performant.

## Data fetching

Prefer:

* TanStack Query / React Query

for server state.

## Forms

Use:

* React Hook Form
* Zod

for form state and validation.

## State

Use local React state for local UI state.

Use a lightweight state solution only when truly necessary.

Do NOT introduce a global state library simply because it exists.

---

# 5. FRONTEND ARCHITECTURE

Use a clean, scalable architecture.

Recommended structure:

```text
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   │
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── notifications/
│   │   └── settings/
│   │
│   ├── projects/
│   │   └── [projectId]/
│   │       ├── overview/
│   │       ├── tasks/
│   │       ├── members/
│   │       └── activity/
│   │
│   ├── layout.tsx
│   └── globals.css
│
├── components/
│   ├── ui/
│   ├── layout/
│   ├── navigation/
│   ├── auth/
│   ├── dashboard/
│   ├── projects/
│   ├── tasks/
│   ├── comments/
│   ├── notifications/
│   └── shared/
│
├── features/
│   ├── auth/
│   ├── projects/
│   ├── tasks/
│   ├── comments/
│   ├── notifications/
│   └── users/
│
├── lib/
│   ├── api/
│   ├── auth/
│   ├── utils/
│   ├── validations/
│   └── constants/
│
├── hooks/
├── types/
├── providers/
└── config/
```

The exact architecture may be improved if there is a strong engineering reason.

Do not over-engineer.

---

# 6. DESIGN SYSTEM FIRST

Before implementing pages, establish a reusable design system.

Create a coherent visual language for:

* colors
* typography
* spacing
* border radius
* shadows
* surfaces
* buttons
* inputs
* cards
* dialogs
* dropdowns
* badges
* avatars
* tabs
* tooltips
* navigation
* tables
* notifications
* task cards
* status indicators

Do NOT independently style every page.

The same component should look and behave consistently everywhere.

---

# 7. VISUAL DIRECTION

The visual identity should feel:

* sophisticated
* minimal
* premium
* technical
* modern
* calm
* focused

Avoid:

* excessive gradients
* neon colors
* excessive glassmorphism
* huge typography
* excessive shadows
* excessive rounded cards
* emoji as UI icons
* inconsistent spacing
* random colors
* visually noisy dashboards

Use color intentionally.

For example:

```text
Primary
Secondary
Success
Warning
Danger
Info
Muted
Background
Surface
Border
Foreground
```

Define semantic design tokens.

Do not scatter arbitrary hex colors throughout the codebase.

---

# 8. DARK MODE

Implement:

* Light mode
* Dark mode

Dark mode must be intentionally designed.

Do not simply invert colors.

Dark mode should have:

* layered surfaces
* readable borders
* correct contrast
* muted text hierarchy
* proper hover states
* subtle highlights

Persist the user's theme preference.

Respect system preference when appropriate.

---

# 9. ANIMATION SYSTEM

The frontend must contain tasteful micro-interactions.

Use animation for:

* route transitions
* sidebar transitions
* dropdowns
* dialogs
* toast notifications
* list entrances
* task status changes
* hover states
* button feedback
* loading states
* skeletons
* notification updates
* modal opening/closing
* mobile navigation
* page transitions where appropriate

Animations must be:

* subtle
* fast
* smooth
* purposeful

Do NOT animate everything.

Do NOT create animations that reduce usability.

Support:

```text
prefers-reduced-motion
```

---

# 10. ICONOGRAPHY

Use Lucide icons consistently.

Never use random Unicode symbols as UI icons.

Do not use emoji for:

* navigation
* buttons
* status indicators
* settings
* actions

Icons must support RTL correctly.

---

# 11. RESPONSIVE DESIGN

The application must be fully responsive.

Support:

* desktop
* laptop
* tablet
* mobile

Do not simply shrink the desktop layout.

Mobile must have intentional UX.

For example:

Desktop:

```text
Sidebar + Main Content
```

Mobile:

```text
Top Bar
      ↓
Content
      ↓
Bottom / Drawer Navigation where appropriate
```

Tables may become:

* cards
* horizontal scroll
* responsive list views

depending on the content.

---

# 12. ACCESSIBILITY

Accessibility is mandatory.

Implement:

* semantic HTML
* keyboard navigation
* visible focus states
* proper labels
* accessible dialogs
* accessible dropdowns
* ARIA where necessary
* sufficient color contrast
* screen-reader-friendly controls
* reduced motion
* proper heading hierarchy

Never use clickable `<div>` where a semantic button/link is appropriate.

---

# 13. AUTHENTICATION

Implement complete authentication UX.

Pages:

```text
/login
/register
```

Features:

* login
* registration
* logout
* authentication persistence
* session restoration
* token refresh
* protected routes
* unauthorized handling

Authentication must integrate with:

```text
/api/v1/auth/register
/api/v1/auth/login
/api/v1/auth/refresh
/api/v1/auth/logout
/api/v1/auth/me
```

Do not assume the exact response shape.

Inspect the backend contract and adapt the frontend API client accordingly.

---

# 14. TOKEN MANAGEMENT

Implement token handling securely.

The frontend must:

* attach authentication to API requests
* handle expired access tokens
* refresh tokens when appropriate
* retry failed requests only when safe
* prevent infinite refresh loops
* logout cleanly when refresh fails

Avoid storing sensitive authentication data in insecure locations unnecessarily.

Prefer secure HTTP-only cookie architecture if supported by the backend.

If the backend uses a different token strategy, adapt to the actual backend implementation.

---

# 15. API CLIENT

Create a centralized API client.

Do NOT call `fetch()` randomly throughout components.

Use a structured API layer.

Example:

```text
lib/api/
├── client.ts
├── auth.ts
├── projects.ts
├── tasks.ts
├── comments.ts
├── notifications.ts
└── users.ts
```

The API client must handle:

* base URL
* authentication
* headers
* JSON serialization
* errors
* status codes
* refresh flow
* request cancellation where appropriate

---

# 16. TYPE SAFETY

TypeScript strict mode should be enabled.

Avoid:

```ts
any
```

unless there is a documented reason.

Define types for:

* User
* Project
* ProjectMember
* Task
* Comment
* Notification
* Activity
* Pagination
* API errors
* Auth responses

If OpenAPI generation from FastAPI is practical, consider generating or deriving API types from the backend schema.

Do not duplicate API contracts manually if a reliable generated solution can be used.

---

# 17. API ERROR HANDLING

The backend uses structured errors such as:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project was not found",
    "details": null
  }
}
```

The frontend must normalize API errors.

Create a predictable frontend error abstraction.

Display:

* user-friendly Persian message
* actionable feedback
* retry option where appropriate

Never expose raw backend stack traces.

---

# 18. GLOBAL ERROR EXPERIENCE

Implement:

* route-level error boundaries
* API error handling
* network error handling
* authentication errors
* permission errors
* validation errors
* server errors
* empty states

Every failure must have a designed UX.

Do NOT leave:

```text
Something went wrong
```

as the only experience.

---

# 19. LOADING EXPERIENCE

Every data-driven page must have proper loading states.

Use:

* skeletons
* placeholders
* progress indicators
* optimistic UI where appropriate

Avoid blank screens.

Avoid spinners everywhere.

Use skeleton layouts that resemble the final content.

---

# 20. EMPTY STATES

Every collection must have a meaningful empty state.

Examples:

No projects:

```text
هنوز پروژه‌ای ندارید
اولین پروژه خود را ایجاد کنید.
[ایجاد پروژه]
```

No tasks:

```text
هنوز تسکی ایجاد نشده است.
یک تسک جدید ایجاد کنید.
```

Empty states should contain:

* illustration/icon
* explanation
* primary action

Do not make empty pages look broken.

---

# 21. TOAST / FEEDBACK SYSTEM

Implement a global notification/toast system.

Use it for:

* successful creation
* successful update
* successful deletion
* authentication errors
* permission errors
* network errors
* background updates

Examples:

```text
پروژه با موفقیت ایجاد شد.
تسک با موفقیت بروزرسانی شد.
تغییرات ذخیره شد.
```

Avoid excessive notifications.

---

# 22. DASHBOARD

Create a polished dashboard.

Route:

```text
/dashboard
```

Include:

### Header

* greeting
* current user
* notifications
* profile menu

### Overview

Useful summary cards:

* total projects
* active tasks
* completed tasks
* overdue tasks

Do not fabricate statistics.

All statistics must come from backend data.

### Recent Tasks

Display:

* task
* project
* status
* priority
* assignee
* due date

### Recent Activity

Display recent project activity.

### Project Overview

Show project progress.

### Notifications

Show recent notifications.

The dashboard should communicate useful information immediately without becoming cluttered.

---

# 23. MAIN NAVIGATION

Create a premium sidebar/navigation system.

Desktop:

```text
Logo
──────────────
داشبورد
پروژه‌ها
اعلان‌ها
تنظیمات
──────────────
User Profile
```

The sidebar must support:

* active state
* hover state
* collapse if appropriate
* smooth animation
* responsive behavior

Mobile navigation must be redesigned appropriately.

---

# 24. PROJECTS PAGE

Route:

```text
/projects
```

Features:

* project list
* search
* sorting
* filters if supported
* create project
* project cards
* project status
* member avatars
* progress

Project cards should be visually rich but not overloaded.

Each project should communicate:

* name
* description
* status
* progress
* task summary
* members
* updated time

---

# 25. CREATE PROJECT

Create a polished dialog/page.

Fields:

* name
* description
* status

Use React Hook Form + Zod.

Handle:

* validation
* loading
* server errors
* success
* cancellation

After successful creation:

* update cache
* show success feedback
* navigate appropriately

Avoid unnecessary full-page reloads.

---

# 26. PROJECT DETAILS

Route:

```text
/projects/[projectId]
```

Use a project-specific layout.

Suggested navigation:

```text
نمای کلی
تسک‌ها
اعضا
فعالیت‌ها
```

The project header should contain:

* project name
* description
* status
* owner
* members
* actions

---

# 27. PROJECT OVERVIEW

Display:

* project progress
* task summary
* recent activity
* members
* upcoming deadlines
* recent tasks

Use lightweight data visualization where useful.

Do not add charts just for decoration.

---

# 28. TASK MANAGEMENT

This is one of the most important parts of the product.

Provide:

### List view

Columns/fields:

* title
* status
* priority
* assignee
* due date
* updated date

### Optional Kanban view

Columns:

```text
TODO
IN_PROGRESS
IN_REVIEW
DONE
CANCELLED
```

Kanban should support smooth interaction.

If drag-and-drop is implemented, it must:

* feel smooth
* update backend state
* handle failure
* revert optimistic updates when necessary
* respect permissions

---

# 29. TASK FILTERS

Implement:

* search
* status
* priority
* assignee
* due date
* sorting

Filters should be reflected in URL query parameters where appropriate.

Example:

```text
/projects/123/tasks?status=IN_PROGRESS&priority=HIGH
```

This allows:

* deep linking
* browser navigation
* shareable views

---

# 30. TASK PAGINATION

Use backend pagination.

Do NOT fetch all tasks and paginate in the browser.

Support:

* page
* page size
* next
* previous

Preserve filter state.

---

# 31. TASK CREATION

Create a polished task form.

Fields:

* title
* description
* status
* priority
* assignee
* due date

Validation must happen client-side for UX and backend-side for correctness.

After creation:

* update relevant queries
* close modal if applicable
* show success feedback
* optionally navigate to task details

---

# 32. TASK DETAILS

Task details should feel like a real productivity application.

Display:

* title
* description
* status
* priority
* assignee
* creator
* due date
* timestamps
* comments
* activity

Actions:

* edit
* delete
* assign
* change status
* change priority

Only show actions the current user is allowed to perform.

But remember:

**Frontend visibility is UX only. Backend authorization remains the source of truth.**

---

# 33. COMMENTS

Create a polished comments section.

Features:

* list comments
* create comment
* edit own comment
* delete own comment

UX should include:

* avatar
* author
* timestamp
* content
* actions
* loading state
* empty state

Use optimistic UI only where safe.

---

# 34. MEMBERS

Project members page:

```text
/projects/[projectId]/members
```

Display:

* avatar
* name
* email
* role
* joined date

Actions based on permissions:

* invite
* change role
* remove member

Roles:

```text
OWNER
ADMIN
MEMBER
VIEWER
```

Frontend must derive visible actions from the current user's permissions.

Do not duplicate authorization logic in a way that becomes a security boundary.

---

# 35. INVITATIONS

Create a polished invitation flow.

Features:

* invite by email
* validation
* loading
* success
* duplicate member handling
* invalid email handling
* permission errors

If the backend exposes invitation status, display it.

---

# 36. NOTIFICATIONS

Create a notification center.

Features:

* unread count
* notification list
* read/unread state
* mark as read
* mark all as read

Notification types may include:

* task assigned
* project invitation
* task status changed
* comment added
* mention

Notifications should have:

* icon
* title
* description
* timestamp
* unread indicator
* relevant navigation target

---

# 37. ACTIVITY FEED

Create a polished activity timeline.

Examples:

```text
علی تسک «طراحی صفحه ورود» را ایجاد کرد.
سارا وضعیت تسک را به «در حال انجام» تغییر داد.
محمد به پروژه اضافه شد.
```

Use timeline styling.

Do not make it visually overwhelming.

---

# 38. USER PROFILE

Create profile UI.

Display:

* avatar
* name
* email
* account information

Support editing fields provided by backend.

Never allow editing server-controlled fields without backend support.

---

# 39. SETTINGS

Create a settings area.

Potential sections:

```text
حساب کاربری
ظاهر
اعلان‌ها
امنیت
```

Only implement functionality supported by the backend.

Do not create fake settings.

---

# 40. ROLE-AWARE UI

The frontend must understand the current user's role.

Example:

```text
OWNER
ADMIN
MEMBER
VIEWER
```

Use role-aware rendering to improve UX.

Examples:

Viewer should not see:

```text
Delete Project
Invite Member
Change Role
```

But again:

This is NOT security.

Backend remains authoritative.

---

# 41. DATA FETCHING STRATEGY

Use TanStack Query for server state.

Create query keys systematically.

Example:

```text
['current-user']
['projects']
['project', projectId]
['project-tasks', projectId, filters]
['task', taskId]
['task-comments', taskId]
['notifications']
['project-activity', projectId]
```

Implement:

* caching
* invalidation
* stale times
* retries where appropriate
* optimistic updates where safe

Avoid unnecessary refetching.

---

# 42. CACHE INVALIDATION

After mutations, update or invalidate the correct queries.

Example:

Create project:

```text
POST project
      ↓
invalidate ['projects']
```

Update task:

```text
PATCH task
      ↓
invalidate:
['task', taskId]
['project-tasks', projectId]
['project', projectId]
```

Do not simply refresh the entire browser.

---

# 43. OPTIMISTIC UI

Use optimistic updates only for interactions where rollback is safe.

Good examples:

* mark notification as read
* toggle task status
* lightweight UI state

When optimistic update fails:

1. restore previous state
2. show error
3. refetch authoritative state

---

# 44. FORMS

All forms must provide:

* labels
* validation
* loading states
* disabled states
* errors
* success feedback
* keyboard accessibility

Use:

```text
React Hook Form
+
Zod
```

Validation messages must be understandable in Persian.

---

# 45. DELETE CONFIRMATIONS

Destructive actions must require confirmation where appropriate.

Examples:

* delete project
* delete task
* remove member
* delete comment

Use accessible dialogs.

Make destructive consequences clear.

---

# 46. SEARCH

Search should feel responsive.

Where backend search exists:

Use the backend.

Do not download everything and filter locally.

Use debounce where appropriate.

Show:

* loading
* no results
* results
* clear search

---

# 47. URL STATE

Use URL query parameters for shareable state where appropriate.

Examples:

```text
?page=2
&status=IN_PROGRESS
&priority=HIGH
&search=frontend
```

Browser back/forward must work naturally.

---

# 48. DATE AND TIME

The backend may provide ISO timestamps.

Create centralized date formatting utilities.

Display Persian-friendly dates.

Consider Jalali/Persian calendar UX where appropriate.

Do not scatter date formatting logic throughout components.

Use a reliable date library if necessary.

Always handle timezone correctly.

---

# 49. PERFORMANCE

The frontend must be performant.

Consider:

* Next.js server/client boundaries
* dynamic imports
* image optimization
* lazy loading
* memoization only where useful
* avoiding unnecessary renders
* efficient query caching
* virtualized lists only when actually necessary

Do not prematurely optimize.

Measure before introducing complexity.

---

# 50. SEO

Public pages should have proper metadata.

Authenticated dashboard pages should have appropriate titles.

Use meaningful page titles:

```text
داشبورد | Project Management Platform
پروژه‌ها | Project Management Platform
```

---

# 51. SECURITY

Frontend security requirements:

* never expose secrets
* never include backend secrets in client bundle
* never trust client-side permissions
* never put private environment variables into `NEXT_PUBLIC_*`
* sanitize/handle user-generated content appropriately
* avoid unsafe HTML rendering
* handle authentication failures correctly

---

# 52. ENVIRONMENT CONFIGURATION

Create:

```text
.env.example
```

Example:

```text
NEXT_PUBLIC_API_URL=
```

Only public configuration should use:

```text
NEXT_PUBLIC_*
```

Never expose:

```text
DATABASE_URL
JWT_SECRET
REDIS_URL
```

to the frontend.

---

# 53. FRONTEND-BACKEND INTEGRATION

The frontend must connect to the backend using:

```text
/api/v1
```

or the configured backend base URL.

Before implementing integration:

1. inspect backend routes
2. inspect OpenAPI schema
3. inspect request schemas
4. inspect response schemas
5. inspect authentication behavior
6. inspect error format
7. inspect pagination format

Do not guess API contracts if the backend source/docs are available.

If backend and frontend contracts disagree:

1. identify the mismatch
2. determine the correct source of truth
3. adapt safely
4. document the change

---

# 54. API CONTRACT CHECKLIST

Before considering a feature complete, verify:

```text
[ ] Correct endpoint
[ ] Correct HTTP method
[ ] Correct request body
[ ] Correct query parameters
[ ] Correct headers
[ ] Correct authentication
[ ] Correct response mapping
[ ] Correct error handling
[ ] Correct loading state
[ ] Correct empty state
[ ] Correct success feedback
[ ] Correct cache invalidation
```

---

# 55. NO MOCK DATA RULE

The following are forbidden in the final application:

```text
const projects = [...]
const tasks = [...]
const notifications = [...]
```

as fake production data.

Do not use:

* fake users
* fake projects
* fake tasks
* fake dashboard metrics

for final application functionality.

If seed data is required for development:

* create proper backend seed data
* document it
* keep it separate from frontend production logic

---

# 56. FRONTEND TESTING

Implement meaningful frontend tests.

At minimum test:

### Components

* forms
* buttons
* dialogs
* task cards
* notification components

### Features

* login flow
* project creation
* task creation
* filtering
* permission-aware UI

### Integration

Test important API-driven flows.

Use appropriate tools such as:

* Vitest
* React Testing Library
* Playwright

The exact combination may be selected by the agent based on the existing project.

Do not create fake tests only to increase coverage.

---

# 57. E2E TESTING

Create critical end-to-end scenarios.

Example:

```text
Register
   ↓
Login
   ↓
Create Project
   ↓
Create Task
   ↓
Assign Task
   ↓
Change Status
   ↓
Add Comment
   ↓
Verify Notification
```

Another scenario:

```text
Viewer Login
   ↓
Open Project
   ↓
View Task
   ↓
Verify destructive actions are unavailable
```

---

# 58. ERROR SCENARIOS TO TEST

Test:

* invalid credentials
* expired authentication
* server unavailable
* 401
* 403
* 404
* 409
* 422
* 429
* 500
* slow network
* empty responses
* failed mutation
* failed optimistic update

Every important scenario must have intentional UX.

---

# 59. RESPONSIVE QA

Verify at minimum:

```text
Mobile
Tablet
Desktop
Large Desktop
```

Check:

* navigation
* dialogs
* forms
* task lists
* project cards
* kanban
* notifications
* tables
* typography
* RTL behavior

---

# 60. VISUAL QA

Before declaring completion, inspect every major page visually.

Check:

* spacing
* alignment
* typography
* color
* contrast
* hierarchy
* animation
* responsiveness
* empty states
* loading states
* errors
* dark mode
* RTL

Do not assume that because the code compiles the UI is finished.

---

# 61. PAGES REQUIRED

At minimum implement:

```text
/login
/register

/dashboard

/projects
/projects/[projectId]
/projects/[projectId]/overview
/projects/[projectId]/tasks
/projects/[projectId]/members
/projects/[projectId]/activity

/notifications

/settings
/settings/profile
/settings/appearance
```

Add additional routes if they improve the product architecture.

---

# 62. COMPONENTS REQUIRED

Create reusable components such as:

```text
AppShell
Sidebar
MobileNavigation
TopBar
UserMenu
NotificationBell
PageHeader
Breadcrumbs
ProjectCard
ProjectStatusBadge
ProjectProgress
TaskCard
TaskTable
TaskBoard
TaskStatusBadge
TaskPriorityBadge
TaskFilters
TaskForm
TaskDetails
CommentList
CommentForm
MemberList
MemberAvatar
RoleBadge
ActivityTimeline
NotificationList
EmptyState
ErrorState
LoadingSkeleton
ConfirmDialog
SearchInput
Pagination
```

Do not create components unnecessarily.

Reuse components aggressively where semantics are shared.

---

# 63. DESIGN QUALITY BAR

A feature is NOT complete simply because:

```text
the API call works
```

A feature is complete only when:

```text
API integration
+
UX
+
UI
+
validation
+
loading state
+
empty state
+
error state
+
responsive behavior
+
accessibility
+
animation where appropriate
+
cache synchronization
```

are all considered.

---

# 64. FRONTEND PHASE PLAN

The agent MUST execute the frontend in these phases.

---

## Phase F0 — Frontend Audit & Architecture

Before writing UI:

1. inspect repository
2. inspect existing frontend
3. inspect backend
4. inspect OpenAPI
5. inspect API routes
6. inspect authentication
7. inspect database-driven entities through backend contracts
8. identify existing reusable components
9. determine what is already implemented
10. create frontend architecture plan
11. create route map
12. create API integration map
13. create component map
14. create design system plan

Do NOT rewrite working code unnecessarily.

At the end:

* provide audit
* provide implementation plan
* provide identified backend/frontend mismatches

STOP.

---

# Phase F1 — Frontend Foundation & Design System

Implement:

* Next.js configuration
* TypeScript strictness
* Tailwind
* shadcn/ui
* Vazirmatn
* RTL
* theme system
* light/dark mode
* design tokens
* global styles
* animation foundation
* reusable UI primitives
* toast system
* loading primitives
* error primitives

Create the application shell foundation.

STOP.

---

# Phase F2 — Application Shell

Implement:

* desktop sidebar
* mobile navigation
* top bar
* user menu
* notification entry point
* breadcrumbs
* responsive layout
* page container system
* navigation active states

The shell must already feel like a polished SaaS application.

STOP.

---

# Phase F3 — API Client & Data Layer

Implement:

* centralized API client
* typed API functions
* authentication integration
* error normalization
* TanStack Query
* query keys
* cache strategy
* mutation patterns
* authentication refresh behavior

Connect to the real backend.

STOP.

---

# Phase F4 — Authentication UX

Implement:

* login
* register
* logout
* protected routes
* session restoration
* token refresh
* validation
* errors
* loading
* success states

Test authentication end-to-end.

STOP.

---

# Phase F5 — Dashboard

Implement complete dashboard:

* statistics
* projects
* recent tasks
* activity
* notifications
* responsive behavior
* skeletons
* empty states
* animations

All data must come from backend.

STOP.

---

# Phase F6 — Projects

Implement:

* project list
* project search
* project creation
* project editing
* project deletion
* project details
* project overview
* project progress
* project members

Connect everything to backend.

STOP.

---

# Phase F7 — Tasks

Implement:

* task list
* task creation
* task editing
* task deletion
* task details
* filters
* search
* sorting
* pagination
* status
* priority
* assignee
* due dates

STOP.

---

# Phase F8 — Advanced Task UX

Implement:

* Kanban board
* drag-and-drop if supported
* optimistic status changes
* animations
* task detail interactions
* responsive task experience
* advanced filters

STOP.

---

# Phase F9 — Members & RBAC UX

Implement:

* members page
* member invitation
* role display
* role management
* remove member
* role-aware UI
* permission-aware actions

STOP.

---

# Phase F10 — Comments & Activity

Implement:

* comments
* edit/delete
* activity timeline
* activity detail
* optimistic interactions where safe

STOP.

---

# Phase F11 — Notifications

Implement:

* notification center
* unread count
* mark read
* mark all read
* notification navigation
* real-time/polling behavior if backend supports it

STOP.

---

# Phase F12 — Settings

Implement:

* profile
* appearance
* theme
* account settings supported by backend

STOP.

---

# Phase F13 — Responsive & Accessibility Pass

Perform complete audit.

Check:

* mobile
* tablet
* desktop
* keyboard
* screen reader semantics
* focus states
* contrast
* reduced motion
* RTL

Fix all issues.

STOP.

---

# Phase F14 — Error / Loading / Empty State Pass

Audit every page and feature.

Every async feature must have:

```text
Loading
Success
Empty
Error
Unauthorized
Forbidden
Not Found
```

where applicable.

Fix everything.

STOP.

---

# Phase F15 — Testing

Implement:

* component tests
* integration tests
* E2E tests
* authentication tests
* project tests
* task tests
* permission tests
* error scenarios

Run the complete suite.

STOP.

---

# Phase F16 — Performance & Production Polish

Audit:

* bundle size
* unnecessary renders
* API calls
* caching
* images
* loading performance
* animations
* accessibility
* client/server boundaries

Fix meaningful issues.

STOP.

---

# Phase F17 — Final Visual QA

Review every major page.

Perform:

* desktop visual review
* mobile visual review
* RTL review
* dark mode review
* interaction review
* animation review

Fix inconsistencies.

STOP.

---

# Phase F18 — Production Readiness

Verify:

```text
[ ] npm install/build works
[ ] TypeScript passes
[ ] lint passes
[ ] tests pass
[ ] E2E passes
[ ] environment variables documented
[ ] API integration works
[ ] authentication works
[ ] no fake production data
[ ] responsive behavior works
[ ] RTL works
[ ] dark mode works
[ ] accessibility reviewed
[ ] Docker frontend works
[ ] production build works
```

STOP.

---

# 65. AGENT EXECUTION RULES

You are responsible for making engineering decisions.

Do not ask unnecessary questions.

If a reasonable decision can be made:

**make it.**

Ask the user only if:

* credentials are required
* an external service requires a decision
* the backend contract is fundamentally ambiguous
* two incompatible architectures are possible

Otherwise proceed.

---

# 66. NEVER BREAK THE BACKEND

The frontend agent must NOT modify backend behavior simply to make frontend implementation easier.

If a backend issue is discovered:

1. identify it
2. document it
3. determine whether a safe backend change is necessary
4. ask only if the change is architectural or destructive

Never silently change backend contracts.

---

# 67. NEVER USE FAKE SUCCESS

Do not implement:

```text
setTimeout(() => success)
```

to simulate backend operations.

Do not pretend an operation succeeded.

The UI must reflect actual API responses.

---

# 68. NEVER IGNORE API ERRORS

Bad:

```text
catch {
  console.log(error)
}
```

Good:

```text
normalize error
→ show user feedback
→ preserve UI state
→ allow retry
```

---

# 69. NO GIANT COMPONENTS

Avoid components containing hundreds or thousands of lines.

Break complex features into meaningful components.

But do not create absurd abstractions such as:

```text
UniversalCardRendererFactory
```

for simple UI.

Prefer understandable architecture.

---

# 70. NO DESIGN DRIFT

Once the design system is established:

Do not randomly introduce:

* new border radius
* new button styles
* new typography
* new colors
* new shadows

unless the design system is intentionally updated.

---

# 71. FINAL UX STANDARD

The final product should make a developer looking at the repository think:

> "This person understands modern frontend engineering and can build a real product."

It should NOT feel like:

> "This is a backend project with a frontend attached to it."

The frontend should be a serious portfolio piece on its own.

---

# 72. FINAL DEFINITION OF DONE

The frontend is complete only when:

### Architecture

* [ ] Clean Next.js architecture
* [ ] TypeScript strict
* [ ] Reusable components
* [ ] Design system
* [ ] API layer
* [ ] Query layer

### UI/UX

* [ ] Premium visual design
* [ ] RTL
* [ ] Persian UI
* [ ] Vazirmatn
* [ ] Responsive
* [ ] Dark mode
* [ ] Animations
* [ ] Micro-interactions
* [ ] Accessibility

### Features

* [ ] Authentication
* [ ] Dashboard
* [ ] Projects
* [ ] Tasks
* [ ] Kanban
* [ ] Comments
* [ ] Members
* [ ] RBAC-aware UI
* [ ] Activity
* [ ] Notifications
* [ ] Settings

### Backend Integration

* [ ] Real API
* [ ] Authentication
* [ ] Token refresh
* [ ] Error handling
* [ ] Pagination
* [ ] Filtering
* [ ] Search
* [ ] Cache synchronization
* [ ] No fake production data

### Quality

* [ ] Loading states
* [ ] Empty states
* [ ] Error states
* [ ] Success states
* [ ] Form validation
* [ ] Accessibility
* [ ] Performance
* [ ] E2E testing

### Production

* [ ] Build passes
* [ ] Lint passes
* [ ] TypeScript passes
* [ ] Tests pass
* [ ] Docker works
* [ ] Environment variables documented

---

# 73. FINAL AGENT INSTRUCTION

You are not merely implementing screens.

You are building the complete frontend product experience.

Think simultaneously as:

```text
Frontend Engineer
+
UI Engineer
+
UX Designer
+
Product Designer
+
Accessibility Engineer
+
Performance Engineer
```

Every page must be connected to the real backend.

Every interaction must have intentional UX.

Every async operation must have loading/error/success behavior.

Every important action must respect the backend's permission model.

Every page must work correctly in RTL.

Every major interface must work on mobile.

Every visual pattern must belong to the application's design system.

Do not stop at "it works".

Make it **feel finished**.

Do not use mock data in the final product.

Do not skip visual QA.

Do not skip responsive QA.

Do not skip accessibility.

Do not skip API integration.

Do not automatically proceed between phases.

At the end of each phase:

1. Explain what was implemented.
2. List important files changed.
3. List API integrations completed.
4. List tests/checks executed.
5. List known issues.
6. Confirm the phase is complete.
7. **STOP.**

Wait for the user to explicitly say:

```text
Continue
```

before starting the next phase.

---

# 🚨 START HERE

**Start with Phase F0 only.**

First inspect the existing frontend and backend.

Do not start rewriting the application immediately.

Understand what already exists.

Then produce:

1. Frontend audit
2. Existing architecture analysis
3. Backend API integration map
4. Route map
5. Component map
6. Design system plan
7. Authentication strategy
8. State management strategy
9. Responsive strategy
10. Phase-by-phase implementation plan

Then STOP and wait for approval.
