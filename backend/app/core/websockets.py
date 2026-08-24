import asyncio
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logging import logger
from app.core.redis import get_redis_client


class ConnectionManager:
    """Manages project WebSocket connections, presence, and event dispatch."""

    def __init__(self) -> None:
        # project_id (str) -> set of active WebSockets
        self.active_rooms: dict[str, set[WebSocket]] = {}
        # project_id (str) -> user_id (str) -> set of WebSockets
        self.user_sockets: dict[str, dict[str, set[WebSocket]]] = {}
        # user_id (str) -> user profile dict
        self.user_profiles: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self,
        project_id: str,
        user_id: str,
        user_data: dict[str, Any],
        websocket: WebSocket,
    ) -> None:
        """Register a new WebSocket connection and update user presence."""
        await websocket.accept()

        async with self._lock:
            if project_id not in self.active_rooms:
                self.active_rooms[project_id] = set()
                self.user_sockets[project_id] = {}

            self.active_rooms[project_id].add(websocket)
            self.user_profiles[user_id] = user_data

            is_first_connection_for_user = (
                user_id not in self.user_sockets[project_id]
                or len(self.user_sockets[project_id][user_id]) == 0
            )

            if user_id not in self.user_sockets[project_id]:
                self.user_sockets[project_id][user_id] = set()
            self.user_sockets[project_id][user_id].add(websocket)

            # Build list of currently online users in this project
            online_users = [
                self.user_profiles[uid]
                for uid in self.user_sockets[project_id].keys()
                if uid in self.user_profiles
            ]

        # 1. Send current presence state directly to newly connected socket
        await self.send_personal_message(
            websocket=websocket,
            event="presence:state",
            project_id=project_id,
            payload={"online_users": online_users},
        )

        # 2. If newly joined (not just extra tab/socket), broadcast presence:joined
        if is_first_connection_for_user:
            await self.broadcast_to_project(
                project_id=project_id,
                event="presence:joined",
                payload={"user_id": user_id, "user": user_data},
            )

    async def disconnect(
        self,
        project_id: str,
        user_id: str,
        websocket: WebSocket,
    ) -> None:
        """Deregister a WebSocket and broadcast presence:left if last socket."""
        user_is_offline = False

        async with self._lock:
            if project_id in self.active_rooms:
                self.active_rooms[project_id].discard(websocket)
                if not self.active_rooms[project_id]:
                    del self.active_rooms[project_id]

            if (
                project_id in self.user_sockets
                and user_id in self.user_sockets[project_id]
            ):
                self.user_sockets[project_id][user_id].discard(websocket)
                if not self.user_sockets[project_id][user_id]:
                    del self.user_sockets[project_id][user_id]
                    user_is_offline = True
                if not self.user_sockets[project_id]:
                    del self.user_sockets[project_id]

        if user_is_offline:
            await self.broadcast_to_project(
                project_id=project_id,
                event="presence:left",
                payload={"user_id": user_id},
            )

    async def send_personal_message(
        self,
        websocket: WebSocket,
        event: str,
        project_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Send direct WebSocket event envelope to a specific connection."""
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        envelope = {
            "event": event,
            "project_id": project_id,
            "payload": payload,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await websocket.send_json(envelope)
        except Exception as e:
            logger.warning("Failed to send WebSocket direct message: %s", e)

    async def broadcast_to_project(
        self,
        project_id: str | uuid.UUID,
        event: str,
        payload: dict[str, Any],
    ) -> None:
        """Broadcast event to all clients in a project room (Redis + Local)."""
        pid_str = str(project_id)
        envelope = {
            "event": event,
            "project_id": pid_str,
            "payload": payload,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # 1. Publish to Redis channel if available
        try:
            client = await get_redis_client()
            channel = f"channel:project:{pid_str}"
            await client.publish(channel, json.dumps(envelope))
            await client.aclose()
        except Exception:
            # Fallback to local in-memory broadcasting if Redis is offline/test mode
            pass

        # 2. Dispatch to local room connections
        await self._dispatch_local(pid_str, envelope)

    async def _dispatch_local(self, project_id: str, envelope: dict[str, Any]) -> None:
        """Send message to all locally connected WebSockets in project room."""
        sockets = list(self.active_rooms.get(project_id, set()))
        if not sockets:
            return

        dead_sockets = set()
        for ws in sockets:
            if ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.send_json(envelope)
                except Exception as e:
                    logger.debug("Failed sending to socket: %s", e)
                    dead_sockets.add(ws)
            else:
                dead_sockets.add(ws)

        if dead_sockets:
            async with self._lock:
                if project_id in self.active_rooms:
                    self.active_rooms[project_id].difference_update(dead_sockets)


# Global singleton connection manager
ws_manager = ConnectionManager()
