from fastapi import APIRouter

from app.api.v1.activity import router as activity_router
from app.api.v1.attachments import router as attachments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.comments import router as comments_router
from app.api.v1.health import router as health_router
from app.api.v1.labels import router as labels_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.projects import router as projects_router
from app.api.v1.search import router as search_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.users import router as users_router
from app.api.v1.websockets import router as websockets_router

api_router = APIRouter()

# Core system endpoints
api_router.include_router(health_router)

# Authentication & Session endpoints
api_router.include_router(auth_router)

# User profile & Management endpoints
api_router.include_router(users_router)

# Project & Workspace endpoints
api_router.include_router(projects_router)

# Task & Workflow endpoints
api_router.include_router(tasks_router)

# Collaboration Comments endpoints
api_router.include_router(comments_router)

# Task Labels & Tagging endpoints
api_router.include_router(labels_router)

# Task File Attachments endpoints
api_router.include_router(attachments_router)

# Global Search & Saved Views endpoints
api_router.include_router(search_router)

# In-App Notifications endpoints
api_router.include_router(notifications_router)

# Activity & Audit log endpoints
api_router.include_router(activity_router)

# Real-Time WebSocket channels
api_router.include_router(websockets_router)
