# Phase F0 — Frontend Audit & Architecture Plan

> **Status:** Complete — awaiting approval to start Phase F1  
> **Date:** 2026-08-25  
> **Source of truth:** `front.md`

---

## 1. Frontend audit

### Verdict

The frontend is a **Next.js 16 + React 19 scaffold** with a full shadcn/ui kit and Persian/RTL root layout foundations. **Almost no product features exist yet.**

| Area | Status |
|------|--------|
| Framework / TypeScript strict | Ready |
| shadcn/ui (~61 components) | Scaffolded, unused by pages |
| Vazirmatn + `lang="fa"` + `dir="rtl"` | Partial (layout only) |
| Design tokens (light/dark CSS vars) | Present in `globals.css` |
| Theme runtime (`next-themes`) | Installed, **not wired** |
| TanStack Query / axios | Installed, **unused** |
| Auth / API client / routes | **Missing** |
| Product pages | **Empty** (default create-next-app home) |
| Forms (RHF + Zod) | **Not installed** |
| Motion / Framer Motion | **Not installed** |
| Tests | **None** |
| Docker | Dev-only (`npm run dev`) |

### Current `src/` tree

```text
src/
├── app/
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx      # Persian metadata, Vazirmatn, RTL
│   └── page.tsx        # English Next.js boilerplate
├── components/ui/      # 61 shadcn primitives
├── hooks/use-mobile.ts
└── lib/utils.ts        # cn() only
```

### What already exists (keep)

- Next.js App Router + TypeScript `strict: true`
- Path alias `@/*` → `./src/*`
- Vazirmatn via `next/font/google`
- Root RTL + Persian metadata template
- shadcn/ui component library (taupe / `base-sera`)
- Light/dark OKLCH design tokens in CSS
- Docker Compose `frontend` service + env vars in root `.env.example`
- Deps ready to wire: `@tanstack/react-query`, `axios`, `next-themes`, `sonner`, `lucide-react`

### What must be built

Everything in `front.md` phases F1–F18: design system wiring, app shell, API layer, auth, dashboard, projects, tasks, kanban, members, comments, activity, notifications, settings, QA, tests, polish.

---

## 2. Existing architecture analysis

| Layer | Finding |
|-------|---------|
| Routing | Only `/` — no route groups, no middleware |
| Providers | None (no QueryClient, ThemeProvider, Toaster) |
| Features | No `features/`, no domain components |
| API | No `lib/api/` |
| Auth | No token storage, refresh, or protected routes |
| State | N/A — no server state wired |
| Config | Env documented at repo root; not consumed in frontend code |

**Decision:** Do **not** rewrite working scaffold pieces (font, tokens, shadcn). Extend them. Replace the English boilerplate home with auth redirect / product entry.

**Packages to add in F1/F3/F4:**

- `react-hook-form`, `@hookform/resolvers`, `zod`
- `motion` (or `framer-motion`)
- Jalali date helper (e.g. `date-fns-jalali` or equivalent) for Persian dates
- Test tooling later (F15): Vitest + RTL + Playwright

---

## 3. Backend API integration map

**Base URL:** `NEXT_PUBLIC_API_URL` → `http://localhost:8000/api/v1`  
**Auth:** Bearer JWT access + opaque refresh in JSON body (no cookies)  
**OpenAPI:** `/api/v1/openapi.json`, Swagger `/docs`

### Auth

| Method | Path | Notes |
|--------|------|-------|
| POST | `/auth/register` | → `{ tokens, user }` |
| POST | `/auth/login` | → `{ tokens, user }` |
| POST | `/auth/refresh` | body: `{ refresh_token }` → new token pair |
| POST | `/auth/logout` | body: `{ refresh_token }` |
| GET | `/auth/me` | Bearer required |

`tokens`: `access_token`, `refresh_token`, `token_type`, `expires_in`

### Users

| Method | Path |
|--------|------|
| GET/PATCH | `/users/me` |
| GET | `/users/{user_id}` |
| GET | `/users?q=&page=&page_size=` |

### Projects & members

| Method | Path |
|--------|------|
| POST/GET | `/projects` |
| GET/PATCH/DELETE | `/projects/{id}` |
| GET/POST | `/projects/{id}/members` |
| PATCH/DELETE | `/projects/{id}/members/{user_id}` |

Create body: `{ name, description? }` — **no project status field** (use `is_archived`).

### Tasks

| Method | Path |
|--------|------|
| POST/GET | `/projects/{id}/tasks` |
| GET/PATCH/DELETE | `/tasks/{id}` |
| PATCH | `/tasks/{id}/reorder` | Kanban: `{ position, status? }` |

Filters: `status`, `priority`, `assignee_id`, `unassigned`, `label_id`, `q`, `due_date_from/to`, `sort_by`, `order`, `page`, `page_size`

### Comments, labels, attachments, activity, notifications, search, WS

| Area | Key paths |
|------|-----------|
| Comments | `/tasks/{id}/comments`, `/comments/{id}` |
| Labels | `/projects/{id}/labels`, `/labels/{id}`, task attach/detach |
| Attachments | multipart `file` on `/tasks/{id}/attachments` |
| Activity | `/projects/{id}/activity`, `/tasks/{id}/activity` |
| Notifications | `/notifications`, unread-count, mark read, mark-all-read |
| Search | `/search/tasks` (+ facets), `/saved-views` |
| WebSocket | `WS /ws/projects/{id}?token=` |

### Error envelope

```json
{ "error": { "code": "NOT_FOUND", "message": "...", "details": null } }
```

### Pagination envelope

```json
{ "items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0 }
```

### Enums (backend truth)

| Enum | Values |
|------|--------|
| `ProjectRole` | `OWNER`, `ADMIN`, `MEMBER`, `VIEWER` |
| `TaskStatus` | `BACKLOG`, `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE` |
| `TaskPriority` | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| `NotificationType` | `task:assigned`, `task:status_changed`, `comment:added`, `user:mentioned`, `project:invited` |

---

## 4. Backend / frontend mismatches (from `front.md`)

| Spec assumption | Backend reality | Frontend approach |
|-----------------|-----------------|-------------------|
| Prefer HTTP-only cookies | Tokens in JSON only | Store access in memory; refresh in `httpOnly`-like safe pattern via secure storage strategy (prefer memory + sessionStorage for refresh; document XSS risk) |
| Project `status` field | `is_archived` boolean | Map UI status to archived/active |
| Task status includes `CANCELLED` | No `CANCELLED` | Use backend statuses only; Kanban columns: BACKLOG → DONE |
| Duplicate `/auth/me` vs `/users/me` | Both return `UserResponse` | Prefer `/auth/me` for session; `/users/me` for profile PATCH |
| Dashboard “stats” endpoints | No dedicated stats API | Derive from projects list + task queries / search facets |
| Invite flow | `POST .../members` with `email` or `user_id` | Build invite UI against this endpoint |

**Do not change backend contracts** to match the frontend spec.

---

## 5. Route map

```text
/                         → redirect to /dashboard or /login
/login                    → (auth)
/register                 → (auth)

/dashboard                → (app) shell
/projects                 → list + create
/projects/[projectId]     → redirect → overview
/projects/[projectId]/overview
/projects/[projectId]/tasks
/projects/[projectId]/members
/projects/[projectId]/activity

/notifications
/settings
/settings/profile
/settings/appearance
```

Optional later: task deep-link `/projects/[projectId]/tasks/[taskId]` (sheet/modal preferred for SaaS feel).

**Middleware:** protect all `(app)` routes; redirect authenticated users away from auth pages.

---

## 6. Target folder architecture

```text
frontend/src/
├── app/
│   ├── (auth)/login|register/
│   ├── (app)/
│   │   ├── layout.tsx          # AppShell
│   │   ├── dashboard/
│   │   ├── projects/...
│   │   ├── notifications/
│   │   └── settings/...
│   ├── layout.tsx
│   ├── globals.css
│   ├── error.tsx / not-found.tsx / loading.tsx
│   └── page.tsx                # redirect
├── components/
│   ├── ui/                     # existing shadcn
│   ├── layout/                 # AppShell, Sidebar, TopBar, MobileNav
│   ├── navigation/
│   ├── auth/
│   ├── dashboard/
│   ├── projects/
│   ├── tasks/
│   ├── comments/
│   ├── notifications/
│   └── shared/                 # EmptyState, ErrorState, PageHeader, ...
├── features/
│   ├── auth/
│   ├── projects/
│   ├── tasks/
│   ├── comments/
│   ├── notifications/
│   └── users/
├── lib/
│   ├── api/                    # client, auth, projects, tasks, ...
│   ├── auth/                   # token store, session helpers
│   ├── utils/
│   ├── validations/
│   ├── dates/                  # Persian/Jalali formatters
│   └── constants/
├── hooks/
├── types/
├── providers/                  # theme, query, auth
└── config/
```

---

## 7. Component map (priority)

**Shell:** `AppShell`, `Sidebar`, `MobileNavigation`, `TopBar`, `UserMenu`, `NotificationBell`, `Breadcrumbs`, `PageHeader`

**Shared:** `EmptyState`, `ErrorState`, `LoadingSkeleton`, `ConfirmDialog`, `SearchInput`, `Pagination`

**Domain:** `ProjectCard`, `ProjectStatusBadge`, `ProjectProgress`, `TaskCard`, `TaskTable`, `TaskBoard`, `TaskStatusBadge`, `TaskPriorityBadge`, `TaskFilters`, `TaskForm`, `TaskDetails`, `CommentList`, `CommentForm`, `MemberList`, `MemberAvatar`, `RoleBadge`, `ActivityTimeline`, `NotificationList`

Reuse shadcn primitives; avoid parallel button/input styles.

---

## 8. Design system plan

**Direction:** Sophisticated, minimal, calm, technical — Linear/Vercel-inspired polish without copying.

**Tokens (extend existing OKLCH vars):**

- Background / Surface / Border / Foreground / Muted
- Primary / Secondary / Success / Warning / Danger / Info
- Sidebar tokens (already present)
- Radius scale: keep shadcn defaults; no random radii
- Motion: short (150–250ms), `prefers-reduced-motion` respected

**Runtime:**

- Wire `next-themes` with `attribute="class"`, persist preference, `suppressHydrationWarning` on `<html>`
- Mount Sonner toaster (Persian messages)
- Enable DirectionProvider for Radix/Base UI where needed
- Set `components.json` `"rtl": true` when regenerating components

**Typography:** Vazirmatn only for UI; fix leftover Geist CSS var references in `globals.css`.

---

## 9. Authentication strategy

1. Login/register → store `access_token` (memory) + `refresh_token` (sessionStorage)
2. Axios/fetch interceptor attaches `Authorization: Bearer`
3. On `401`, single-flight refresh via `/auth/refresh`; retry original request
4. Refresh failure → clear session → redirect `/login`
5. Bootstrap: restore refresh token → refresh or `/auth/me`
6. Logout: POST `/auth/logout` with refresh token → clear local state
7. Next.js middleware: cookie mirror **or** client guard + layout redirect (prefer lightweight httpOnly cookie bridge only if we add a thin BFF later; **default: client AuthProvider + protected layout** matching current backend)

No fake auth. No mock users.

---

## 10. State management strategy

| Concern | Tool |
|---------|------|
| Server state | TanStack Query |
| Auth session | React context + token module |
| Theme | `next-themes` |
| Forms | React Hook Form + Zod |
| URL filters | `nuqs` or native `useSearchParams` |
| Local UI | `useState` |

**Query key examples:**

```text
['current-user']
['projects', filters]
['project', projectId]
['project-tasks', projectId, filters]
['task', taskId]
['task-comments', taskId]
['notifications', filters]
['project-activity', projectId]
['project-members', projectId]
```

Invalidate narrowly after mutations. Optimistic updates only for safe ops (mark notification read, kanban status).

---

## 11. Responsive strategy

| Breakpoint | Navigation |
|------------|------------|
| Desktop (`lg+`) | Collapsible sidebar + main |
| Tablet | Collapsible / sheet sidebar |
| Mobile | Top bar + sheet/drawer nav; tables → cards; kanban horizontal scroll |

Touch targets ≥ 44px. Dialogs full-screen on small viewports where appropriate.

---

## 12. Phase-by-phase implementation plan

| Phase | Scope | Stop gate |
|-------|-------|-----------|
| **F0** | Audit & plan (this doc) | ✅ Done |
| **F1** | Foundation: tokens, RTL polish, theme, toast, primitives, providers skeleton | Wait |
| **F2** | App shell: sidebar, mobile nav, top bar, breadcrumbs | Wait |
| **F3** | API client, types, Query, refresh interceptor | Wait |
| **F4** | Auth UX + protected routes E2E | Wait |
| **F5** | Dashboard (derived real data) | Wait |
| **F6** | Projects CRUD + overview | Wait |
| **F7** | Tasks list/filters/pagination/CRUD | Wait |
| **F8** | Kanban + reorder + optimistic UX | Wait |
| **F9** | Members + RBAC-aware UI | Wait |
| **F10** | Comments + activity | Wait |
| **F11** | Notifications (+ polling/WS if ready) | Wait |
| **F12** | Settings (profile + appearance) | Wait |
| **F13** | Responsive & a11y pass | Wait |
| **F14** | Error/loading/empty pass | Wait |
| **F15** | Tests (unit/integration/E2E) | Wait |
| **F16** | Performance polish | Wait |
| **F17** | Visual QA | Wait |
| **F18** | Production readiness checklist | Wait |

Each phase ends with: summary, files changed, API integrations, checks, known issues, then **STOP** until user says `Continue`.

---

## 13. Known risks / follow-ups

1. No dedicated dashboard metrics API — compute carefully; avoid N+1 where possible (batch with search facets / limited task queries).
2. Token-in-JS storage XSS risk — sanitize user HTML; never `dangerouslySetInnerHTML` for comments without sanitization.
3. Docker frontend is dev-only — production multi-stage build in F18.
4. `components.json` has `"rtl": false` — align during F1.
5. Missing RHF/Zod/motion deps — install in F1.
6. WebSocket optional until F11; HTTP polling acceptable interim for notifications.

---

## 14. Phase F0 confirmation

- [x] Repository inspected
- [x] Existing frontend audited
- [x] Backend API contracts mapped
- [x] OpenAPI / routes / auth / entities understood
- [x] Route map defined
- [x] Component map defined
- [x] Design system plan defined
- [x] Auth & state strategies defined
- [x] Mismatches documented (no silent backend changes)
- [x] Phase plan F1–F18 ready

**Phase F0 is complete. Waiting for explicit `Continue` to start Phase F1.**
