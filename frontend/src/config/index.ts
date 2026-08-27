export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
    wsUrl: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws",
  },
  app: {
    name: "پلتفرم مدیریت پروژه",
    description: "پلتفرم حرفه‌ای مدیریت پروژه و تیم",
  },
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
} as const;
