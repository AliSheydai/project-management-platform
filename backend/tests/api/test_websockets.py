import uuid

import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


async def _setup_project_and_users(
    async_client: AsyncClient,
) -> tuple[str, dict, str, dict, dict]:
    """Helper to register owner & member, create project, and return tokens."""
    # Register Owner
    o_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": f"ws_owner_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!",
            "first_name": "WSOwner",
            "last_name": "Admin",
        },
    )
    assert o_res.status_code == 201
    owner_token = o_res.json()["tokens"]["access_token"]
    owner_user = o_res.json()["user"]

    # Register Member
    m_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": f"ws_member_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!",
            "first_name": "WSMember",
            "last_name": "Dev",
        },
    )
    assert m_res.status_code == 201
    member_token = m_res.json()["tokens"]["access_token"]
    member_user = m_res.json()["user"]

    # Create Project
    p_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Real-time WS Project"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert p_res.status_code == 201
    project = p_res.json()

    # Add Member to Project
    mem_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert mem_res.status_code == 201

    return owner_token, owner_user, member_token, member_user, project


async def test_ws_authentication_failures(async_client: AsyncClient) -> None:
    """Test missing, invalid, and non-member WebSocket connection attempts."""
    owner_token, _, _, _, project = await _setup_project_and_users(async_client)

    # Register outsider user
    out_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": f"outsider_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!",
            "first_name": "Outsider",
            "last_name": "User",
        },
    )
    outsider_token = out_res.json()["tokens"]["access_token"]

    test_client = TestClient(app)

    # 1. Missing token
    with pytest.raises(WebSocketDisconnect) as exc:
        with test_client.websocket_connect(f"/api/v1/ws/projects/{project['id']}"):
            pass
    assert exc.value.code == 1008

    # 2. Invalid token
    with pytest.raises(WebSocketDisconnect) as exc:
        with test_client.websocket_connect(
            f"/api/v1/ws/projects/{project['id']}?token=invalid.jwt.token"
        ):
            pass
    assert exc.value.code == 1008

    # 3. Non-member (Outsider) forbidden
    with pytest.raises(WebSocketDisconnect) as exc:
        with test_client.websocket_connect(
            f"/api/v1/ws/projects/{project['id']}?token={outsider_token}"
        ):
            pass
    assert exc.value.code == 1008


async def test_ws_presence_and_ping_pong(async_client: AsyncClient) -> None:
    """Test WebSocket connection, initial presence state, and ping-pong heartbeat."""
    owner_token, _, member_token, member_user, project = await _setup_project_and_users(
        async_client
    )

    test_client = TestClient(app)

    # Member connects
    with test_client.websocket_connect(
        f"/api/v1/ws/projects/{project['id']}?token={member_token}"
    ) as ws:
        # 1. Receive presence:state on join
        msg = ws.receive_json()
        assert msg["event"] == "presence:state"
        assert msg["project_id"] == project["id"]
        assert "online_users" in msg["payload"]
        assert len(msg["payload"]["online_users"]) >= 1

        # 2. Receive presence:joined broadcast
        join_msg = ws.receive_json()
        assert join_msg["event"] == "presence:joined"
        assert join_msg["payload"]["user_id"] == member_user["id"]

        # 3. Send ping action and receive pong
        ws.send_json({"action": "ping"})
        pong_msg = ws.receive_json()
        assert pong_msg["event"] == "pong"
        assert "timestamp" in pong_msg["payload"]


async def test_ws_task_and_comment_broadcasting(async_client: AsyncClient) -> None:
    """Test task creation, update, and comment real-time broadcasting."""
    owner_token, _, member_token, member_user, project = await _setup_project_and_users(
        async_client
    )

    test_client = TestClient(app)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Member stays connected via WebSocket
    with test_client.websocket_connect(
        f"/api/v1/ws/projects/{project['id']}?token={member_token}"
    ) as ws:
        # Consume initial presence:state and presence:joined
        init_state = ws.receive_json()
        assert init_state["event"] == "presence:state"

        join_state = ws.receive_json()
        assert join_state["event"] == "presence:joined"
        assert join_state["payload"]["user_id"] == member_user["id"]

        # 1. Owner creates task via REST
        t_res = await async_client.post(
            f"/api/v1/projects/{project['id']}/tasks",
            json={"title": "WebSocket Realtime Task"},
            headers=owner_headers,
        )
        assert t_res.status_code == 201
        task = t_res.json()

        # Member socket receives task:created
        ws_created = ws.receive_json()
        assert ws_created["event"] == "task:created"
        assert ws_created["payload"]["task"]["title"] == "WebSocket Realtime Task"

        # 2. Owner updates task via REST
        up_res = await async_client.patch(
            f"/api/v1/tasks/{task['id']}",
            json={"status": "IN_PROGRESS"},
            headers=owner_headers,
        )
        assert up_res.status_code == 200

        # Member socket receives task:updated
        ws_updated = ws.receive_json()
        assert ws_updated["event"] == "task:updated"
        assert ws_updated["payload"]["task"]["status"] == "IN_PROGRESS"

        # 3. Owner adds comment via REST
        c_res = await async_client.post(
            f"/api/v1/tasks/{task['id']}/comments",
            json={"content": "Real-time collaboration test!"},
            headers=owner_headers,
        )
        assert c_res.status_code == 201

        # Member socket receives comment:added
        ws_comment = ws.receive_json()
        assert ws_comment["event"] == "comment:added"
        assert (
            ws_comment["payload"]["comment"]["content"]
            == "Real-time collaboration test!"
        )
