from httpx import AsyncClient


async def _create_user(client: AsyncClient, email: str, name: str) -> tuple[str, dict]:
    """Helper to register user and return token and user dict."""
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


async def test_activity_logging_and_feeds(async_client: AsyncClient) -> None:
    """Test automatic activity tracking on task and comment events."""
    owner_token, owner_user = await _create_user(
        async_client, "activity.owner@example.com", "Owner"
    )
    member_token, member_user = await _create_user(
        async_client, "activity.member@example.com", "Member"
    )
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # 1. Create project
    p_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Activity Feed Project"},
        headers=owner_headers,
    )
    project = p_res.json()
    project_id = project["id"]

    # Add member
    await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers=owner_headers,
    )

    # 2. Create Task -> Logs 'task:created'
    t_res = await async_client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Audit Tracking Task"},
        headers=owner_headers,
    )
    task = t_res.json()
    task_id = task["id"]

    # 3. Update Task Status -> Logs 'task:status_changed'
    await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "IN_PROGRESS"},
        headers=owner_headers,
    )

    # 4. Assign Task to member -> Logs 'task:assigned'
    await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"assignee_id": member_user["id"]},
        headers=owner_headers,
    )

    # 5. Add Comment -> Logs 'comment:added'
    await async_client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"content": "Looks good so far!"},
        headers=owner_headers,
    )

    # 6. Fetch Project Activity Feed
    proj_act_res = await async_client.get(
        f"/api/v1/projects/{project_id}/activity",
        headers=owner_headers,
    )
    assert proj_act_res.status_code == 200
    proj_act = proj_act_res.json()
    assert proj_act["total"] >= 4
    actions = [item["action"] for item in proj_act["items"]]
    assert "comment:added" in actions
    assert "task:assigned" in actions
    assert "task:status_changed" in actions
    assert "task:created" in actions

    # 7. Fetch Task Specific Activity Feed
    task_act_res = await async_client.get(
        f"/api/v1/tasks/{task_id}/activity",
        headers=owner_headers,
    )
    assert task_act_res.status_code == 200
    task_act = task_act_res.json()
    assert task_act["total"] >= 4
    for item in task_act["items"]:
        assert item["task_id"] == task_id
        assert item["user"]["id"] == owner_user["id"]
