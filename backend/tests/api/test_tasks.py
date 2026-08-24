from httpx import AsyncClient


async def _create_authenticated_user(
    client: AsyncClient, email: str, name: str
) -> tuple[str, dict]:
    """Helper to register and return token and user dict."""
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "first_name": name,
            "last_name": "User",
        },
    )
    assert res.status_code == 201
    return res.json()["tokens"]["access_token"], res.json()["user"]


async def _create_project(
    client: AsyncClient, token: str, name: str = "Test Project"
) -> dict:
    """Helper to create a project."""
    res = await client.post(
        "/api/v1/projects",
        json={"name": name, "description": "Workspace for tasks"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    return res.json()


async def test_create_task_success(async_client: AsyncClient) -> None:
    """Test POST /api/v1/projects/{project_id}/tasks creates a task."""
    owner_token, owner_user = await _create_authenticated_user(
        async_client, "owner.task@example.com", "Owner"
    )
    project = await _create_project(async_client, owner_token)

    task_payload = {
        "title": "Build Auth Middleware",
        "description": "Implement JWT and token rotation",
        "status": "TODO",
        "priority": "HIGH",
    }
    response = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json=task_payload,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Build Auth Middleware"
    assert data["status"] == "TODO"
    assert data["priority"] == "HIGH"
    assert data["project_id"] == project["id"]
    assert data["creator"]["id"] == owner_user["id"]
    assert data["assignee"] is None
    assert data["position"] == 1000.0


async def test_task_assignment_validation(async_client: AsyncClient) -> None:
    """Test task assignment to valid member vs non-member."""
    owner_token, _ = await _create_authenticated_user(
        async_client, "owner.assign@example.com", "Owner"
    )
    member_token, member_user = await _create_authenticated_user(
        async_client, "member.assign@example.com", "Member"
    )
    outsider_token, outsider_user = await _create_authenticated_user(
        async_client, "outsider.assign@example.com", "Outsider"
    )

    project = await _create_project(async_client, owner_token)

    # Add member to project
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # 1. Assign to valid member -> Success
    valid_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Design Database Schema",
            "assignee_id": member_user["id"],
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert valid_res.status_code == 201
    assert valid_res.json()["assignee"]["id"] == member_user["id"]

    # 2. Assign to non-member outsider -> 400 Bad Request
    invalid_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Invalid Task Assignment",
            "assignee_id": outsider_user["id"],
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert invalid_res.status_code == 400
    assert "member of this project" in invalid_res.json()["error"]["message"]


async def test_list_tasks_filtering_and_sorting(
    async_client: AsyncClient,
) -> None:
    """Test listing tasks with status, priority, search, and ordering."""
    token, _ = await _create_authenticated_user(
        async_client, "filter.user@example.com", "Filter"
    )
    project = await _create_project(async_client, token)
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple tasks
    await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Frontend Landing Page",
            "status": "TODO",
            "priority": "LOW",
        },
        headers=headers,
    )
    await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Backend API Service",
            "status": "IN_PROGRESS",
            "priority": "URGENT",
        },
        headers=headers,
    )
    await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Database Optimization",
            "status": "DONE",
            "priority": "HIGH",
        },
        headers=headers,
    )

    # 1. Filter by status
    status_res = await async_client.get(
        f"/api/v1/projects/{project['id']}/tasks?status=IN_PROGRESS",
        headers=headers,
    )
    assert status_res.status_code == 200
    assert status_res.json()["total"] == 1
    assert status_res.json()["items"][0]["title"] == "Backend API Service"

    # 2. Filter by priority
    priority_res = await async_client.get(
        f"/api/v1/projects/{project['id']}/tasks?priority=URGENT",
        headers=headers,
    )
    assert priority_res.status_code == 200
    assert priority_res.json()["total"] == 1
    assert priority_res.json()["items"][0]["priority"] == "URGENT"

    # 3. Search keyword
    search_res = await async_client.get(
        f"/api/v1/projects/{project['id']}/tasks?q=Optimization",
        headers=headers,
    )
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1
    assert search_res.json()["items"][0]["title"] == "Database Optimization"


async def test_update_and_reorder_task(async_client: AsyncClient) -> None:
    """Test updating task attributes, workflow transitions, and Kanban reordering."""
    token, _ = await _create_authenticated_user(
        async_client, "updater.task@example.com", "Updater"
    )
    project = await _create_project(async_client, token)
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Draft Architecture"},
        headers=headers,
    )
    task_id = create_res.json()["id"]

    # Workflow transition: TODO -> IN_PROGRESS -> DONE
    update_res = await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Finalize Architecture",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
        },
        headers=headers,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Finalize Architecture"
    assert updated["status"] == "IN_PROGRESS"
    assert updated["priority"] == "HIGH"

    # Reorder board position
    reorder_res = await async_client.patch(
        f"/api/v1/tasks/{task_id}/reorder",
        json={"position": 2500.0, "status": "DONE"},
        headers=headers,
    )
    assert reorder_res.status_code == 200
    reordered = reorder_res.json()
    assert reordered["position"] == 2500.0
    assert reordered["status"] == "DONE"


async def test_delete_task(async_client: AsyncClient) -> None:
    """Test DELETE /api/v1/tasks/{task_id} removes task."""
    token, _ = await _create_authenticated_user(
        async_client, "deleter.task@example.com", "Deleter"
    )
    project = await _create_project(async_client, token)
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Temporary Task"},
        headers=headers,
    )
    task_id = create_res.json()["id"]

    # Delete task
    del_res = await async_client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify task no longer exists
    get_res = await async_client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 404


async def test_task_rbac_enforcement(async_client: AsyncClient) -> None:
    """Test RBAC permissions on task creation, editing, and deletion."""
    owner_token, _ = await _create_authenticated_user(
        async_client, "task.owner@example.com", "Owner"
    )
    member_token, member_user = await _create_authenticated_user(
        async_client, "task.member@example.com", "Member"
    )
    viewer_token, viewer_user = await _create_authenticated_user(
        async_client, "task.viewer@example.com", "Viewer"
    )
    outsider_token, _ = await _create_authenticated_user(
        async_client, "task.outsider@example.com", "Outsider"
    )

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

    project = await _create_project(async_client, owner_token)

    # Add Member and Viewer to project
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers=owner_headers,
    )
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": viewer_user["id"], "role": "VIEWER"},
        headers=owner_headers,
    )

    # 1. Viewer cannot create task (403)
    viewer_create = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Viewer Task"},
        headers=viewer_headers,
    )
    assert viewer_create.status_code == 403

    # 2. Member can create task
    member_create = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Member Created Task"},
        headers=member_headers,
    )
    assert member_create.status_code == 201
    task_id = member_create.json()["id"]

    # 3. Viewer cannot edit task (403)
    viewer_edit = await async_client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers=viewer_headers,
    )
    assert viewer_edit.status_code == 403

    # 4. Member cannot delete task (403)
    member_delete = await async_client.delete(
        f"/api/v1/tasks/{task_id}", headers=member_headers
    )
    assert member_delete.status_code == 403

    # 5. Outsider cannot view task (403)
    outsider_get = await async_client.get(
        f"/api/v1/tasks/{task_id}", headers=outsider_headers
    )
    assert outsider_get.status_code == 403

    # 6. Owner can delete task (204)
    owner_delete = await async_client.delete(
        f"/api/v1/tasks/{task_id}", headers=owner_headers
    )
    assert owner_delete.status_code == 204
