# Frontend — Project Management Platform

Persian/RTL Next.js App Router frontend connected to the FastAPI backend.

## Stack

- Next.js 16 + React 19 + TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Query + Axios + Zustand (auth)
- React Hook Form + Zod
- Vazirmatn + `dir="rtl"`

## Setup

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Backend must be available at `NEXT_PUBLIC_API_URL`.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm start` | Start production server |
| `npm run lint` | ESLint |
| `npm test` | Unit tests (Vitest) |

## Docker

Development (compose at repo root) uses `npm run dev`.

Production image:

```bash
docker build -t pm-frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  .
docker run -p 3000:3000 pm-frontend
```

## Auth

JWT Bearer tokens from `/auth/login` and `/auth/register`. Access token in memory; refresh token in `sessionStorage`. Protected app routes use client-side `AppShell` guard.

## Routes

- `/login`, `/register`
- `/dashboard`
- `/projects`, `/projects/[id]/overview|tasks|members|activity`
- `/notifications`
- `/settings/profile`, `/settings/appearance`
