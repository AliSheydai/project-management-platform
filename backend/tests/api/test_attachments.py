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


async def _create_project_and_task(
    client: AsyncClient, token: str
) -> tuple[dict, dict]:
    """Helper to create project and task."""
    headers = {"Authorization": f"Bearer {token}"}
    p_res = await client.post(
        "/api/v1/projects",
        json={"name": "Attachment Project"},
        headers=headers,
    )
    assert p_res.status_code == 201
    project = p_res.json()

    t_res = await client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Task for attachments"},
        headers=headers,
    )
    assert t_res.status_code == 201
    return project, t_res.json()


async def test_upload_list_and_download_attachment(
    async_client: AsyncClient,
) -> None:
    """Test uploading, listing, and downloading task attachments."""
    owner_token, _ = await _create_user(async_client, "owner.att@example.com", "Owner")
    project, task = await _create_project_and_task(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    file_content = b"%PDF-1.4 Mock PDF Content For Project Testing"
    files = {
        "file": ("spec.pdf", file_content, "application/pdf"),
    }

    # 1. Upload attachment
    up_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=headers,
    )
    assert up_res.status_code == 201
    attachment = up_res.json()
    assert attachment["file_name"] == "spec.pdf"
    assert attachment["content_type"] == "application/pdf"
    assert attachment["file_size"] == len(file_content)
    assert attachment["uploader"]["email"] == "owner.att@example.com"
    attachment_id = attachment["id"]

    # 2. List attachments
    list_res = await async_client.get(
        f"/api/v1/tasks/{task['id']}/attachments",
        headers=headers,
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == attachment_id

    # 3. Download attachment
    dl_res = await async_client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=headers,
    )
    assert dl_res.status_code == 200
    assert dl_res.content == file_content
    assert "application/pdf" in dl_res.headers["content-type"]

    # 4. Delete attachment
    del_res = await async_client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=headers,
    )
    assert del_res.status_code == 204

    # 5. Verify deleted
    get_res = await async_client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=headers,
    )
    assert get_res.status_code == 404


async def test_invalid_file_type_rejected(async_client: AsyncClient) -> None:
    """Test disallowed MIME types return 400 Bad Request."""
    owner_token, _ = await _create_user(
        async_client, "owner.badtype@example.com", "Owner"
    )
    _, task = await _create_project_and_task(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    files = {
        "file": ("malicious.exe", b"MZBinaryData", "application/x-dosexec"),
    }
    res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=headers,
    )
    assert res.status_code == 400
    assert "not allowed" in res.json()["error"]["message"]


async def test_attachment_rbac_viewer_restricted(
    async_client: AsyncClient,
) -> None:
    """Test VIEWER role cannot upload or delete attachments."""
    owner_token, _ = await _create_user(
        async_client, "owner.rbac.att@example.com", "Owner"
    )
    viewer_token, viewer_user = await _create_user(
        async_client, "viewer.att@example.com", "Viewer"
    )
    project, task = await _create_project_and_task(async_client, owner_token)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Add viewer to project
    await async_client.post(
        f"/api/v1/projects/{project['id']}/members",
        json={"user_id": viewer_user["id"], "role": "VIEWER"},
        headers=owner_headers,
    )

    # Viewer attempts upload -> 403 Forbidden
    files = {
        "file": ("test.png", b"\x89PNG\r\n\x1a\nFakeImage", "image/png"),
    }
    up_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=viewer_headers,
    )
    assert up_res.status_code == 403

    # Owner uploads
    owner_up = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=owner_headers,
    )
    assert owner_up.status_code == 201
    attachment_id = owner_up.json()["id"]

    # Viewer can download/view
    dl_res = await async_client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=viewer_headers,
    )
    assert dl_res.status_code == 200

    # Viewer attempts to delete -> 403 Forbidden
    del_res = await async_client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=viewer_headers,
    )
    assert del_res.status_code == 403


async def test_attachment_size_limit_exceeded(
    async_client: AsyncClient,
) -> None:
    """Test uploading file exceeding MAX_FILE_SIZE_BYTES returns 400."""
    owner_token, _ = await _create_user(
        async_client, "owner.toobig@example.com", "Owner"
    )
    _, task = await _create_project_and_task(async_client, owner_token)
    headers = {"Authorization": f"Bearer {owner_token}"}

    # 26 MB dummy payload
    oversized_bytes = b"0" * (26 * 1024 * 1024)
    files = {
        "file": ("large_archive.zip", oversized_bytes, "application/zip"),
    }
    res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=headers,
    )
    assert res.status_code == 400
    assert "exceeds max allowed limit" in res.json()["error"]["message"]


async def test_non_member_cannot_download_attachment(
    async_client: AsyncClient,
) -> None:
    """Test non-member user cannot download attachment from private project."""
    owner_token, _ = await _create_user(async_client, "owner.priv@example.com", "Owner")
    outsider_token, _ = await _create_user(
        async_client, "outsider@example.com", "Outsider"
    )
    _, task = await _create_project_and_task(async_client, owner_token)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

    files = {
        "file": ("doc.txt", b"Confidential Project Plan", "text/plain"),
    }
    up_res = await async_client.post(
        f"/api/v1/tasks/{task['id']}/attachments",
        files=files,
        headers=owner_headers,
    )
    assert up_res.status_code == 201
    attachment_id = up_res.json()["id"]

    # Outsider attempts download -> 403 Forbidden
    dl_res = await async_client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=outsider_headers,
    )
    assert dl_res.status_code == 403
