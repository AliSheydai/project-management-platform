import json
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.core.security import decode_access_token
from app.core.websockets import ws_manager
from app.modules.projects.models import ProjectMember
from app.modules.users.models import User

router = APIRouter(tags=["Real-Time WebSockets"])


async def authenticate_ws(
    websocket: WebSocket,
    token: str | None,
    db: AsyncSession,
) -> User | None:
    """Validate JWT token from query params or headers."""
    auth_token = token
    if not auth_token:
        # Check authorization header
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]

    if not auth_token:
        return None

    try:
        payload = decode_access_token(auth_token)
        sub = payload.get("sub")
        if not sub:
            return None
        user_id = uuid.UUID(sub)
    except Exception:
        return None

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        return None

    return user


@router.websocket("/ws/projects/{project_id}")
async def project_events_websocket(
    websocket: WebSocket,
    project_id: uuid.UUID,
    token: Annotated[str | None, Query()] = None,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Project-scoped WebSocket connection with presence and real-time events."""
    user = await authenticate_ws(websocket, token, db)
    if not user:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Unauthorized: Invalid or missing token",
        )
        return

    # Check project membership
    if not user.is_superuser:
        mem_stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        mem_res = await db.execute(mem_stmt)
        if not mem_res.scalar_one_or_none():
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Forbidden: Not a member of this project",
            )
            return

    pid_str = str(project_id)
    uid_str = str(user.id)
    user_info = {
        "id": uid_str,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar_url": user.avatar_url,
    }

    await ws_manager.connect(
        project_id=pid_str,
        user_id=uid_str,
        user_data=user_info,
        websocket=websocket,
    )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await ws_manager.send_personal_message(
                        websocket=websocket,
                        event="pong",
                        project_id=pid_str,
                        payload={"timestamp": datetime.now(UTC).isoformat()},
                    )
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected: %s from %s", uid_str, pid_str)
    except Exception as e:
        logger.warning("WebSocket connection exception: %s", e)
    finally:
        await ws_manager.disconnect(
            project_id=pid_str,
            user_id=uid_str,
            websocket=websocket,
        )
