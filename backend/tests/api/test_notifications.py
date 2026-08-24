from httpx import AsyncClient


async def _create_user(client: AsyncClient, email: str, name: str) -> tuple[str, dict]:
    """Helper to register and return token and user dict."""
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "first_name": name,
            "last_name": "Test",
        },
    )
    assert res.status_code == 201
    return res.json()["tokens"]["access_token"], res.json()["user"]


async def _create_project_with_member(
    client: AsyncClient, owner_token: str, member_user: dict
) -> dict:
    """Helper to create a project and add member."""
    p_res = await client.post(
        "/api/v1/projects",
        json={"name": "Notification Project"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert p_res.status_code == 201
    project = p_res.json()

    m_res = await client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert m_res.status_code == 201
    return project


async def test_task_assignment_and_status_notifications(
    async_client: AsyncClient,
) -> None:
    """Test notifications are triggered on task assignment and status updates."""
    owner_token, _ = await _create_user(
        async_client, "owner.notif@example.com", "Owner"
    )
    member_token, member_user = await _create_user(
        async_client, "member.notif@example.com", "DevMember"
    )
    project = await _create_project_with_member(async_client, owner_token, member_user)

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # 1. Owner assigns task to Member
    t_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Build WebSocket Gateway",
            "assignee_id": member_user["id"],
        },
        headers=owner_headers,
    )
    assert t_res.status_code == 201
    task = t_res.json()

    # 2. Member checks notifications
    m_notifs = await async_client.get(
        "/api/v1/notifications",
        headers=member_headers,
    )
    assert m_notifs.status_code == 200
    m_data = m_notifs.json()
    assert m_data["total"] == 1
    assert m_data["items"][0]["type"] == "task:assigned"
    assert "Build WebSocket Gateway" in m_data["items"][0]["title"]

    # 3. Member updates task status to IN_PROGRESS
    up_res = await async_client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"status": "IN_PROGRESS"},
        headers=member_headers,
    )
    assert up_res.status_code == 200

    # 4. Owner receives status update notification
    o_notifs = await async_client.get(
        "/api/v1/notifications",
        headers=owner_headers,
    )
    assert o_notifs.status_code == 200
    o_data = o_notifs.json()
    assert o_data["total"] == 1
    assert o_data["items"][0]["type"] == "task:status_changed"


async def test_comments_and_mentions_notifications(
    async_client: AsyncClient,
) -> None:
    """Test notifications are triggered on comments and @mentions."""
    owner_token, _ = await _create_user(
        async_client, "owner.commnotif@example.com", "Owner"
    )
    member_token, member_user = await _create_user(
        async_client, "member.mention@example.com", "MentionMe"
    )
    project = await _create_project_with_member(async_client, owner_token, member_user)

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # Owner creates task (unassigned)
    t_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Review DB Indexing"},
        headers=owner_headers,
    )
    assert t_res.status_code == 201
    task = t_res.json()

    # Owner comments with mention: @member.mention@example.com
    c_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={
            "content": "Hey @member.mention@example.com please check query performance!"
        },
        headers=owner_headers,
    )
    assert c_res.status_code == 201

    # Member checks notifications (should receive user:mentioned)
    m_notifs = await async_client.get(
        "/api/v1/notifications",
        headers=member_headers,
    )
    assert m_notifs.status_code == 200
    m_data = m_notifs.json()
    assert m_data["total"] == 1
    assert m_data["items"][0]["type"] == "user:mentioned"


async def test_read_status_and_unread_counts(async_client: AsyncClient) -> None:
    """Test marking notifications as read and unread count queries."""
    owner_token, _ = await _create_user(
        async_client, "owner.readtest@example.com", "Owner"
    )
    member_token, member_user = await _create_user(
        async_client, "member.readtest@example.com", "ReadMember"
    )
    project = await _create_project_with_member(async_client, owner_token, member_user)

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # Generate 2 assignment notifications
    await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Task 1", "assignee_id": member_user["id"]},
        headers=owner_headers,
    )
    await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Task 2", "assignee_id": member_user["id"]},
        headers=owner_headers,
    )

    # 1. Check unread count = 2
    count_res = await async_client.get(
        "/api/v1/notifications/unread-count",
        headers=member_headers,
    )
    assert count_res.status_code == 200
    assert count_res.json()["unread_count"] == 2

    # 2. Get notification ID and mark 1 as read
    list_res = await async_client.get(
        "/api/v1/notifications",
        headers=member_headers,
    )
    notif_id = list_res.json()["items"][0]["id"]

    patch_res = await async_client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers=member_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_read"] is True

    # 3. Check unread count = 1
    c2 = await async_client.get(
        "/api/v1/notifications/unread-count",
        headers=member_headers,
    )
    assert c2.json()["unread_count"] == 1

    # 4. Mark all as read
    mark_all = await async_client.post(
        "/api/v1/notifications/mark-all-read",
        headers=member_headers,
    )
    assert mark_all.status_code == 200

    # 5. Check unread count = 0
    c3 = await async_client.get(
        "/api/v1/notifications/unread-count",
        headers=member_headers,
    )
    assert c3.json()["unread_count"] == 0

    # 6. Delete notification
    del_res = await async_client.delete(
        f"/api/v1/notifications/{notif_id}",
        headers=member_headers,
    )
    assert del_res.status_code == 204
