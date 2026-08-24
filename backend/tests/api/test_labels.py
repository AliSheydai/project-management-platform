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


async def _create_project(client: AsyncClient, token: str) -> dict:
    """Helper to create project."""
    res = await client.post(
        "/api/v1/projects",
        json={"name": "Labels Test Workspace"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    return res.json()


async def test_create_and_list_labels(async_client: AsyncClient) -> None:
    """Test POST and GET /projects/{project_id}/labels."""
    owner_token, _ = await _create_user(async_client, "owner.lbl@example.com", "Owner")
    project = await _create_project(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    # 1. Create label
    c_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/labels",
        json={
            "name": "Bug",
            "color": "#EF4444",
            "description": "High priority issue",
        },
        headers=headers,
    )
    assert c_res.status_code == 201
    label = c_res.json()
    assert label["name"] == "Bug"
    assert label["color"] == "#EF4444"
    assert label["project_id"] == project["id"]

    # 2. List labels
    l_res = await async_client.get(
        f"/api/v1/projects/{project['id']}/labels",
        headers=headers,
    )
    assert l_res.status_code == 200
    list_data = l_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["name"] == "Bug"


async def test_duplicate_label_name_rejected(async_client: AsyncClient) -> None:
    """Test duplicate label name in same project returns 409 Conflict."""
    owner_token, _ = await _create_user(async_client, "owner.dup@example.com", "Owner")
    project = await _create_project(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    # Create label
    await async_client.post(
        f"/api/v1/projects/{project['id']}/labels",
        json={"name": "Feature", "color": "#3B82F6"},
        headers=headers,
    )

    # Duplicate create
    dup_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/labels",
        json={"name": "Feature", "color": "#10B981"},
        headers=headers,
    )
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["error"]["message"]


async def test_update_and_delete_label(async_client: AsyncClient) -> None:
    """Test PATCH and DELETE /labels/{label_id}."""
    owner_token, _ = await _create_user(
        async_client, "owner.updlbl@example.com", "Owner"
    )
    project = await _create_project(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    c_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/labels",
        json={"name": "Initial Name", "color": "#6B7280"},
        headers=headers,
    )
    label_id = c_res.json()["id"]

    # Update label
    upd_res = await async_client.patch(
        f"/api/v1/labels/{label_id}",
        json={"name": "Updated Name", "color": "#F59E0B"},
        headers=headers,
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Updated Name"
    assert upd_res.json()["color"] == "#F59E0B"

    # Delete label
    del_res = await async_client.delete(f"/api/v1/labels/{label_id}", headers=headers)
    assert del_res.status_code == 204


async def test_attach_detach_and_filter_labels_on_tasks(
    async_client: AsyncClient,
) -> None:
    """Test associating labels with tasks and filtering project tasks by label."""
    owner_token, _ = await _create_user(
        async_client, "owner.tasklbl@example.com", "Owner"
    )
    project = await _create_project(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    # Create label
    lbl_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/labels",
        json={"name": "Backend", "color": "#8B5CF6"},
        headers=headers,
    )
    label_id = lbl_res.json()["id"]

    # Create Task 1 with label
    t1_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={
            "title": "Task with label",
            "label_ids": [label_id],
            "custom_fields": {"priority_score": 95},
        },
        headers=headers,
    )
    assert t1_res.status_code == 201
    task1 = t1_res.json()
    assert len(task1["labels"]) == 1
    assert task1["labels"][0]["id"] == label_id
    assert task1["custom_fields"]["priority_score"] == 95

    # Create Task 2 without label
    t2_res = await async_client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Task without label"},
        headers=headers,
    )
    assert t2_res.status_code == 201

    # Filter tasks by label
    filtered_res = await async_client.get(
        f"/api/v1/projects/{project['id']}/tasks?label_id={label_id}",
        headers=headers,
    )
    assert filtered_res.status_code == 200
    filtered = filtered_res.json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["title"] == "Task with label"

    # Detach label from Task 1
    detach_res = await async_client.delete(
        f"/api/v1/tasks/{task1['id']}/labels/{label_id}",
        headers=headers,
    )
    assert detach_res.status_code == 200

    # Re-fetch task
    get_task = await async_client.get(f"/api/v1/tasks/{task1['id']}", headers=headers)
    assert len(get_task.json()["labels"]) == 0
