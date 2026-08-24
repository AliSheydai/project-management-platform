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


async def test_create_project_success(async_client: AsyncClient) -> None:
    """Test POST /api/v1/projects creates project and assigns owner."""
    token, user = await _create_authenticated_user(
        async_client, "owner.proj@example.com", "Project"
    )

    proj_payload = {
        "name": "Mission Alpha",
        "description": "Initial platform mission",
    }
    response = await async_client.post(
        "/api/v1/projects",
        json=proj_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mission Alpha"
    assert data["description"] == "Initial platform mission"
    assert data["owner_id"] == user["id"]
    assert data["is_archived"] is False
    assert data["current_user_role"] == "OWNER"
    assert data["members_count"] == 1


async def test_list_and_search_projects(async_client: AsyncClient) -> None:
    """Test listing user projects with search query and pagination."""
    token, _ = await _create_authenticated_user(
        async_client, "lister@example.com", "List"
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 projects
    await async_client.post(
        "/api/v1/projects", json={"name": "Frontend Portal"}, headers=headers
    )
    await async_client.post(
        "/api/v1/projects", json={"name": "Backend API"}, headers=headers
    )
    await async_client.post(
        "/api/v1/projects", json={"name": "Mobile Client"}, headers=headers
    )

    # List all
    list_res = await async_client.get("/api/v1/projects", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 3

    # Search keyword
    search_res = await async_client.get("/api/v1/projects?q=Backend", headers=headers)
    assert search_res.status_code == 200
    items = search_res.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Backend API"


async def test_get_project_detail(async_client: AsyncClient) -> None:
    """Test GET /api/v1/projects/{project_id} returns detailed project."""
    token, user = await _create_authenticated_user(
        async_client, "detail.user@example.com", "Detail"
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Detailed Project",
            "description": "Details description",
        },
        headers=headers,
    )
    project_id = create_res.json()["id"]

    detail_res = await async_client.get(
        f"/api/v1/projects/{project_id}", headers=headers
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == project_id
    assert detail["owner"]["email"] == "detail.user@example.com"
    assert len(detail["members"]) == 1
    assert detail["members"][0]["role"] == "OWNER"
    assert detail["members"][0]["user"]["id"] == user["id"]


async def test_update_project(async_client: AsyncClient) -> None:
    """Test PATCH /api/v1/projects/{project_id} updates project info."""
    token, _ = await _create_authenticated_user(
        async_client, "patcher@example.com", "Patcher"
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        "/api/v1/projects", json={"name": "Before Update"}, headers=headers
    )
    project_id = create_res.json()["id"]

    update_res = await async_client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "After Update",
            "description": "Updated Description",
            "is_archived": True,
        },
        headers=headers,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "After Update"
    assert updated["description"] == "Updated Description"
    assert updated["is_archived"] is True


async def test_delete_project(async_client: AsyncClient) -> None:
    """Test DELETE /api/v1/projects/{project_id} deletes workspace."""
    token, _ = await _create_authenticated_user(
        async_client, "deleter@example.com", "Deleter"
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        "/api/v1/projects", json={"name": "To Delete"}, headers=headers
    )
    project_id = create_res.json()["id"]

    del_res = await async_client.delete(
        f"/api/v1/projects/{project_id}", headers=headers
    )
    assert del_res.status_code == 204

    # Verify deleted
    get_res = await async_client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert get_res.status_code == 404


async def test_add_list_and_update_members(async_client: AsyncClient) -> None:
    """Test adding member, listing members, and updating member role."""
    owner_token, _ = await _create_authenticated_user(
        async_client, "owner.team@example.com", "Owner"
    )
    _, member_user = await _create_authenticated_user(
        async_client, "developer.team@example.com", "Dev"
    )

    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Create project
    create_res = await async_client.post(
        "/api/v1/projects", json={"name": "Team Space"}, headers=owner_headers
    )
    project_id = create_res.json()["id"]

    # Add member
    add_res = await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": "developer.team@example.com", "role": "MEMBER"},
        headers=owner_headers,
    )
    assert add_res.status_code == 201
    assert add_res.json()["role"] == "MEMBER"
    assert add_res.json()["user"]["email"] == "developer.team@example.com"

    # Duplicate add must fail (409)
    dup_res = await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": "developer.team@example.com", "role": "MEMBER"},
        headers=owner_headers,
    )
    assert dup_res.status_code == 409

    # List members
    list_members_res = await async_client.get(
        f"/api/v1/projects/{project_id}/members", headers=owner_headers
    )
    assert list_members_res.status_code == 200
    members = list_members_res.json()
    assert len(members) == 2

    # Update role to ADMIN
    update_role_res = await async_client.patch(
        f"/api/v1/projects/{project_id}/members/{member_user['id']}",
        json={"role": "ADMIN"},
        headers=owner_headers,
    )
    assert update_role_res.status_code == 200
    assert update_role_res.json()["role"] == "ADMIN"


async def test_member_leave_and_sole_owner_protection(
    async_client: AsyncClient,
) -> None:
    """Test self-removal from project and sole owner protection."""
    owner_token, owner_user = await _create_authenticated_user(
        async_client, "sole.owner@example.com", "SoleOwner"
    )
    member_token, member_user = await _create_authenticated_user(
        async_client, "leaving.member@example.com", "Leaver"
    )

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Leave Workspace"},
        headers=owner_headers,
    )
    project_id = create_res.json()["id"]

    # Sole owner cannot leave or be removed
    sole_res = await async_client.delete(
        f"/api/v1/projects/{project_id}/members/{owner_user['id']}",
        headers=owner_headers,
    )
    assert sole_res.status_code == 409
    assert "sole project owner" in sole_res.json()["error"]["message"].lower()

    # Add member
    await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers=owner_headers,
    )

    # Member leaves
    leave_res = await async_client.delete(
        f"/api/v1/projects/{project_id}/members/{member_user['id']}",
        headers=member_headers,
    )
    assert leave_res.status_code == 200

    # Member can no longer view project
    view_res = await async_client.get(
        f"/api/v1/projects/{project_id}", headers=member_headers
    )
    assert view_res.status_code == 403


async def test_rbac_role_permissions_enforcement(
    async_client: AsyncClient,
) -> None:
    """Test RBAC permission enforcement across VIEWER, ADMIN, and OWNER."""
    owner_token, _ = await _create_authenticated_user(
        async_client, "rbac.owner@example.com", "Owner"
    )
    admin_token, admin_user = await _create_authenticated_user(
        async_client, "rbac.admin@example.com", "Admin"
    )
    viewer_token, viewer_user = await _create_authenticated_user(
        async_client, "rbac.viewer@example.com", "Viewer"
    )

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Owner creates project
    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "RBAC Test Space"},
        headers=owner_headers,
    )
    project_id = create_res.json()["id"]

    # Add Admin and Viewer
    await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": admin_user["id"], "role": "ADMIN"},
        headers=owner_headers,
    )
    await async_client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": viewer_user["id"], "role": "VIEWER"},
        headers=owner_headers,
    )

    # 1. VIEWER checks
    # Viewer can view
    assert (
        await async_client.get(f"/api/v1/projects/{project_id}", headers=viewer_headers)
    ).status_code == 200
    # Viewer cannot edit (403)
    assert (
        await async_client.patch(
            f"/api/v1/projects/{project_id}",
            json={"name": "Hacked"},
            headers=viewer_headers,
        )
    ).status_code == 403
    # Viewer cannot invite (403)
    assert (
        await async_client.post(
            f"/api/v1/projects/{project_id}/members",
            json={"email": "nobody@example.com"},
            headers=viewer_headers,
        )
    ).status_code == 403

    # 2. ADMIN checks
    # Admin can edit project
    admin_patch = await async_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "Admin Updated"},
        headers=admin_headers,
    )
    assert admin_patch.status_code == 200

    # Admin cannot delete project (403)
    admin_del = await async_client.delete(
        f"/api/v1/projects/{project_id}", headers=admin_headers
    )
    assert admin_del.status_code == 403

    # Admin cannot change member role (403)
    admin_role_change = await async_client.patch(
        f"/api/v1/projects/{project_id}/members/{viewer_user['id']}",
        json={"role": "ADMIN"},
        headers=admin_headers,
    )
    assert admin_role_change.status_code == 403


async def test_non_member_cannot_access_project(
    async_client: AsyncClient,
) -> None:
    """Test that users with no membership are completely denied access (403)."""
    owner_token, _ = await _create_authenticated_user(
        async_client, "secret.owner@example.com", "SecretOwner"
    )
    outsider_token, _ = await _create_authenticated_user(
        async_client, "outsider@example.com", "Outsider"
    )

    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Confidential"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    project_id = create_res.json()["id"]

    # Outsider attempts access
    response = await async_client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
