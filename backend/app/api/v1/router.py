from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.users import router as users_router

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
