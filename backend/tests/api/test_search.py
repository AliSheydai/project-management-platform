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


async def _create_project(client: AsyncClient, token: str, name: str) -> dict:
    """Helper to create a project."""
    res = await client.post(
        "/api/v1/projects",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    return res.json()


async def _create_task(
    client: AsyncClient,
    token: str,
    project_id: str,
    title: str,
    status: str = "TODO",
    priority: str = "MEDIUM",
) -> dict:
    """Helper to create a task."""
    res = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": title, "status": status, "priority": priority},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    return res.json()


async def test_cross_project_search_isolation(
    async_client: AsyncClient,
) -> None:
    """Test cross-project search scopes results to user's accessible projects."""
    user1_token, _ = await _create_user(
        async_client, "search.user1@example.com", "User1"
    )
    user2_token, _ = await _create_user(
        async_client, "search.user2@example.com", "User2"
    )

    # User 1 creates Project 1 and Project 2
    p1 = await _create_project(async_client, user1_token, "Project Alpha")
    p2 = await _create_project(async_client, user1_token, "Project Beta")
    await _create_task(async_client, user1_token, p1["id"], "Alpha Secret Mission")
    await _create_task(async_client, user1_token, p2["id"], "Beta Secret Blueprint")

    # User 2 creates Project 3
    p3 = await _create_project(async_client, user2_token, "Project Gamma")
    await _create_task(async_client, user2_token, p3["id"], "Gamma Secret Strategy")

    # User 1 searches keyword "Secret"
    u1_search = await async_client.get(
        "/api/v1/search/tasks?q=Secret",
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert u1_search.status_code == 200
    u1_data = u1_search.json()
    assert u1_data["total"] == 2
    titles = [item["title"] for item in u1_data["items"]]
    assert "Alpha Secret Mission" in titles
    assert "Beta Secret Blueprint" in titles
    assert "Gamma Secret Strategy" not in titles


async def test_advanced_filters_and_facets(async_client: AsyncClient) -> None:
    """Test search multi-status, priority filtering, and facet counts."""
    token, _ = await _create_user(async_client, "search.filters@example.com", "Filters")
    p = await _create_project(async_client, token, "Filter Workspace")
    headers = {"Authorization": f"Bearer {token}"}

    # Seed tasks
    await _create_task(
        async_client,
        token,
        p["id"],
        "Frontend Bug Fix",
        status="TODO",
        priority="HIGH",
    )
    await _create_task(
        async_client,
        token,
        p["id"],
        "Backend Refactor",
        status="IN_PROGRESS",
        priority="HIGH",
    )
    await _create_task(
        async_client,
        token,
        p["id"],
        "Documentation update",
        status="DONE",
        priority="LOW",
    )

    # 1. Search multi-status + priority
    res = await async_client.get(
        f"/api/v1/search/tasks?project_id={p['id']}&status=TODO&status=IN_PROGRESS&priority=HIGH",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert data["facets"]["status_counts"].get("TODO") == 1
    assert data["facets"]["status_counts"].get("IN_PROGRESS") == 1
    assert data["facets"]["priority_counts"].get("HIGH") == 2


async def test_saved_views_crud(async_client: AsyncClient) -> None:
    """Test creating, listing, updating, and deleting saved search views."""
    token, _ = await _create_user(
        async_client, "savedviews.user@example.com", "SavedView"
    )
    p = await _create_project(async_client, token, "View Workspace")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create saved view
    c_res = await async_client.post(
        "/api/v1/saved-views",
        json={
            "name": "High Priority Backlog",
            "project_id": p["id"],
            "filters": {"priority": ["HIGH", "URGENT"], "status": ["TODO"]},
            "is_default": True,
        },
        headers=headers,
    )
    assert c_res.status_code == 201
    view = c_res.json()
    assert view["name"] == "High Priority Backlog"
    assert view["is_default"] is True
    view_id = view["id"]

    # 2. List saved views
    l_res = await async_client.get(
        f"/api/v1/saved-views?project_id={p['id']}",
        headers=headers,
    )
    assert l_res.status_code == 200
    assert l_res.json()["total"] == 1
    assert l_res.json()["items"][0]["id"] == view_id

    # 3. Update saved view
    upd_res = await async_client.patch(
        f"/api/v1/saved-views/{view_id}",
        json={"name": "All Urgent Issues"},
        headers=headers,
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "All Urgent Issues"

    # 4. Delete saved view
    del_res = await async_client.delete(
        f"/api/v1/saved-views/{view_id}",
        headers=headers,
    )
    assert del_res.status_code == 204

    # 5. Verify list is empty
    l2_res = await async_client.get(
        f"/api/v1/saved-views?project_id={p['id']}",
        headers=headers,
    )
    assert l2_res.status_code == 200
    assert l2_res.json()["total"] == 0
