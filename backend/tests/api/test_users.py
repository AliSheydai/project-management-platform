import uuid

from httpx import AsyncClient


async def test_get_my_user_profile(async_client: AsyncClient) -> None:
    """Test GET /api/v1/users/me returns authenticated user."""
    reg_payload = {
        "email": "user.me@example.com",
        "password": "Password123!",
        "first_name": "Me",
        "last_name": "Profile",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user.me@example.com"
    assert data["full_name"] == "Me Profile"


async def test_update_my_profile_details(async_client: AsyncClient) -> None:
    """Test PATCH /api/v1/users/me updates name and avatar."""
    reg_payload = {
        "email": "update.me@example.com",
        "password": "Password123!",
        "first_name": "Original",
        "last_name": "Name",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    update_payload = {
        "first_name": "Updated",
        "last_name": "User",
        "avatar_url": "https://example.com/new_avatar.png",
    }
    patch_res = await async_client.patch(
        "/api/v1/users/me",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"
    assert data["full_name"] == "Updated User"
    assert data["avatar_url"] == "https://example.com/new_avatar.png"


async def test_update_password_and_login(async_client: AsyncClient) -> None:
    """Test updating password in profile and authenticating with the new password."""
    reg_payload = {
        "email": "pwd.change@example.com",
        "password": "OldPassword123!",
        "first_name": "Pwd",
        "last_name": "Tester",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    # Change password
    patch_res = await async_client.patch(
        "/api/v1/users/me",
        json={"password": "BrandNewPassword789!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200

    # Login with old password must fail
    old_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "pwd.change@example.com", "password": "OldPassword123!"},
    )
    assert old_login.status_code == 401

    # Login with new password must succeed
    new_login = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "pwd.change@example.com",
            "password": "BrandNewPassword789!",
        },
    )
    assert new_login.status_code == 200


async def test_get_user_by_id(async_client: AsyncClient) -> None:
    """Test GET /api/v1/users/{user_id} returns target user profile."""
    reg_payload = {
        "email": "target.user@example.com",
        "password": "Password123!",
        "first_name": "Target",
        "last_name": "User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    user_id = reg_res.json()["user"]["id"]
    token = reg_res.json()["tokens"]["access_token"]

    # Query target user
    get_res = await async_client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == user_id
    assert data["email"] == "target.user@example.com"


async def test_get_user_by_id_not_found(async_client: AsyncClient) -> None:
    """Test GET /api/v1/users/{user_id} with unknown UUID returns 404."""
    reg_payload = {
        "email": "caller@example.com",
        "password": "Password123!",
        "first_name": "Caller",
        "last_name": "User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    random_id = uuid.uuid4()
    get_res = await async_client.get(
        f"/api/v1/users/{random_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 404
    assert get_res.json()["error"]["code"] == "NOT_FOUND"


async def test_search_and_list_users(async_client: AsyncClient) -> None:
    """Test GET /api/v1/users searches by keyword with pagination."""
    # Register 2 distinct users
    user_a = {
        "email": "developer.alpha@example.com",
        "password": "Password123!",
        "first_name": "Sarah",
        "last_name": "Connor",
    }
    user_b = {
        "email": "developer.beta@example.com",
        "password": "Password123!",
        "first_name": "Kyle",
        "last_name": "Reese",
    }
    res_a = await async_client.post("/api/v1/auth/register", json=user_a)
    token = res_a.json()["tokens"]["access_token"]
    await async_client.post("/api/v1/auth/register", json=user_b)

    # Search keyword matching 'Sarah'
    search_res = await async_client.get(
        "/api/v1/users?q=Sarah",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search_res.status_code == 200
    data = search_res.json()
    assert "items" in data
    assert data["total"] >= 1
    assert any(u["email"] == "developer.alpha@example.com" for u in data["items"])
    assert not any(u["email"] == "developer.beta@example.com" for u in data["items"])
