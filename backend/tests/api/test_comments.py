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


async def _create_project_and_task(
    client: AsyncClient, token: str
) -> tuple[dict, dict]:
    """Helper to create a project and a task."""
    p_res = await client.post(
        "/api/v1/projects",
        json={"name": "Comments Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert p_res.status_code == 201
    project = p_res.json()

    t_res = await client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Task for Comments"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert t_res.status_code == 201
    task = t_res.json()
    return project, task


async def test_create_and_list_comments(async_client: AsyncClient) -> None:
    """Test POST and GET /tasks/{task_id}/comments."""
    owner_token, owner_user = await _create_user(
        async_client, "owner.comm@example.com", "Owner"
    )
    _, task = await _create_project_and_task(async_client, owner_token)

    # Post a comment
    post_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"content": "Please review this implementation."},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert post_res.status_code == 201
    data = post_res.json()
    assert data["content"] == "Please review this implementation."
    assert data["author"]["id"] == owner_user["id"]
    assert data["task_id"] == task["id"]

    # List comments
    list_res = await async_client.get(
        f"/api/v1/tasks/{task['id']}/comments",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["content"] == "Please review this implementation."


async def test_edit_comment_author_only(async_client: AsyncClient) -> None:
    """Test editing a comment is restricted to the author."""
    owner_token, _ = await _create_user(
        async_client, "owner.editc@example.com", "Owner"
    )
    member_token, member_user = await _create_user(
        async_client, "member.editc@example.com", "Member"
    )
    project, task = await _create_project_and_task(async_client, owner_token)

    # Add member to project
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": member_user["id"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Member posts comment
    comm_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"content": "Initial draft feedback"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert comm_res.status_code == 201
    comment_id = comm_res.json()["id"]

    # Owner tries to edit member's comment -> 403 Forbidden
    owner_edit = await async_client.patch(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Tampered content"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_edit.status_code == 403

    # Member edits their own comment -> 200 OK
    member_edit = await async_client.patch(
        f"/api/v1/comments/{comment_id}",
        json={"content": "Updated draft feedback"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert member_edit.status_code == 200
    assert member_edit.json()["content"] == "Updated draft feedback"


async def test_delete_comment_author_and_admin(
    async_client: AsyncClient,
) -> None:
    """Test comment deletion permissions."""
    owner_token, _ = await _create_user(async_client, "owner.delc@example.com", "Owner")
    member1_token, member1_user = await _create_user(
        async_client, "member1.delc@example.com", "Member1"
    )
    member2_token, member2_user = await _create_user(
        async_client, "member2.delc@example.com", "Member2"
    )

    project, task = await _create_project_and_task(async_client, owner_token)

    for user in [member1_user, member2_user]:
        await async_client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"user_id": user["id"], "role": "MEMBER"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )

    # Member1 posts comment
    comm_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"content": "Comment to be deleted"},
        headers={"Authorization": f"Bearer {member1_token}"},
    )
    assert comm_res.status_code == 201
    comment_id = comm_res.json()["id"]

    # Member2 tries to delete Member1's comment -> 403 Forbidden
    m2_del = await async_client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {member2_token}"},
    )
    assert m2_del.status_code == 403

    # Project Owner deletes Member1's comment -> 204 No Content
    owner_del = await async_client.delete(
        f"/api/v1/comments/{comment_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_del.status_code == 204


async def test_viewer_cannot_comment(async_client: AsyncClient) -> None:
    """Test that VIEWER role is blocked from creating comments."""
    owner_token, _ = await _create_user(async_client, "owner.vc@example.com", "Owner")
    viewer_token, viewer_user = await _create_user(
        async_client, "viewer.vc@example.com", "Viewer"
    )
    project, task = await _create_project_and_task(async_client, owner_token)

    # Add viewer to project
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": viewer_user["id"], "role": "VIEWER"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Viewer tries to post comment -> 403 Forbidden
    res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"content": "Viewer comment attempt"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403
