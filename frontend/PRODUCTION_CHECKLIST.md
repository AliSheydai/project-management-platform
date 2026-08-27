# Frontend Production Readiness (F18)

## Checklist

- [x] `npm install` works
- [x] `npm run build` passes
- [x] TypeScript passes (via Next build)
- [x] Unit tests (`npm test`) for permissions + API errors
- [x] Environment variables documented (`.env.example`)
- [x] Real API integration (no mock production data)
- [x] Authentication UX (login/register/logout/restore/refresh)
- [x] RTL + Vazirmatn
- [x] Dark mode (`next-themes`)
- [x] Responsive shell (sidebar + mobile sheet)
- [x] Loading / empty / error states on main features
- [x] `prefers-reduced-motion` in `globals.css`
- [x] Production Dockerfile (`output: "standalone"`)
- [ ] Full Playwright E2E suite (optional follow-up)
- [ ] Manual visual QA on real devices

## Manual smoke test

1. Start backend + frontend
2. Register a new user → lands on dashboard
3. Create project → overview / tasks / members / activity
4. Create task → kanban drag → detail sheet comments
5. Invite member (second account) → role change
6. Toggle dark mode in settings
7. Logout → login again with refresh restore
