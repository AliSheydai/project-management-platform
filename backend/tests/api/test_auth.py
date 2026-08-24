from httpx import AsyncClient


async def test_register_user_success(async_client: AsyncClient) -> None:
    """Test registering a new user successfully returns token pair and user profile."""
    payload = {
        "email": "alice@example.com",
        "password": "SecurePassword123!",
        "first_name": "Alice",
        "last_name": "Smith",
        "avatar_url": "https://example.com/alice.png",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Check tokens structure
    assert "tokens" in data
    tokens = data["tokens"]
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] > 0

    # Check user structure
    assert "user" in data
    user = data["user"]
    assert user["email"] == "alice@example.com"
    assert user["first_name"] == "Alice"
    assert user["last_name"] == "Smith"
    assert user["full_name"] == "Alice Smith"
    assert user["avatar_url"] == "https://example.com/alice.png"
    assert user["is_active"] is True
    assert user["is_superuser"] is False
    assert "password" not in user
    assert "password_hash" not in user


async def test_register_duplicate_email(async_client: AsyncClient) -> None:
    """Test duplicate registration returns 409 Conflict."""
    payload = {
        "email": "bob@example.com",
        "password": "SecurePassword123!",
        "first_name": "Bob",
        "last_name": "Jones",
    }
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate registration with same email (uppercase to test normalization)
    payload_dup = {
        "email": "BOB@EXAMPLE.COM",
        "password": "AnotherPassword456!",
        "first_name": "Robert",
        "last_name": "Jones",
    }
    res2 = await async_client.post("/api/v1/auth/register", json=payload_dup)
    assert res2.status_code == 409
    error_data = res2.json()
    assert error_data["error"]["code"] == "CONFLICT"


async def test_register_validation_error(async_client: AsyncClient) -> None:
    """Test registering with invalid inputs returns 422 Unprocessable Entity."""
    # Password too short (< 8 chars)
    payload_short_pw = {
        "email": "charlie@example.com",
        "password": "short",
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    res1 = await async_client.post("/api/v1/auth/register", json=payload_short_pw)
    assert res1.status_code == 422

    # Invalid email format
    payload_bad_email = {
        "email": "not-an-email",
        "password": "ValidPassword123!",
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    res2 = await async_client.post("/api/v1/auth/register", json=payload_bad_email)
    assert res2.status_code == 422


async def test_login_success(async_client: AsyncClient) -> None:
    """Test login with valid credentials."""
    register_payload = {
        "email": "david@example.com",
        "password": "MySecretPassword123!",
        "first_name": "David",
        "last_name": "Miller",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "david@example.com",
        "password": "MySecretPassword123!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert data["user"]["email"] == "david@example.com"


async def test_login_invalid_credentials(async_client: AsyncClient) -> None:
    """Test login with wrong password or non-existent user returns 401 Unauthorized."""
    register_payload = {
        "email": "eve@example.com",
        "password": "ValidPassword123!",
        "first_name": "Eve",
        "last_name": "Taylor",
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    # Wrong password
    res_wrong_pw = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "eve@example.com", "password": "WrongPassword!"},
    )
    assert res_wrong_pw.status_code == 401
    assert res_wrong_pw.json()["error"]["code"] == "UNAUTHORIZED"

    # Non-existent email
    res_no_user = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "AnyPassword123!"},
    )
    assert res_no_user.status_code == 401
    assert res_no_user.json()["error"]["code"] == "UNAUTHORIZED"


async def test_get_current_user_profile(async_client: AsyncClient) -> None:
    """Test GET /api/v1/auth/me returns profile for authenticated user."""
    register_payload = {
        "email": "frank@example.com",
        "password": "SecurePassword123!",
        "first_name": "Frank",
        "last_name": "Castle",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=register_payload)
    access_token = reg_res.json()["tokens"]["access_token"]

    # Authenticated call
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "frank@example.com"
    assert me_data["full_name"] == "Frank Castle"


async def test_get_current_user_unauthorized(async_client: AsyncClient) -> None:
    """Test GET /api/v1/auth/me without or with invalid credentials returns 401."""
    # No auth header
    res_no_auth = await async_client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401
    assert res_no_auth.json()["error"]["code"] == "UNAUTHORIZED"

    # Invalid token
    headers = {"Authorization": "Bearer invalid_garbage_token"}
    res_bad_token = await async_client.get("/api/v1/auth/me", headers=headers)
    assert res_bad_token.status_code == 401
    assert res_bad_token.json()["error"]["code"] == "UNAUTHORIZED"


async def test_refresh_token_rotation_and_revocation(
    async_client: AsyncClient,
) -> None:
    """Test refresh token rotation and revocation."""
    reg_payload = {
        "email": "grace@example.com",
        "password": "SecurePassword123!",
        "first_name": "Grace",
        "last_name": "Hopper",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    initial_refresh_token = reg_res.json()["tokens"]["refresh_token"]

    # First refresh succeeds
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    new_refresh_token = new_tokens["refresh_token"]

    # Verify new access token works
    new_access_token = new_tokens["access_token"]
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert me_res.status_code == 200

    # Reusing the old (rotated) refresh token must fail with 401
    reuse_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert reuse_res.status_code == 401
    assert reuse_res.json()["error"]["code"] == "UNAUTHORIZED"

    # Second refresh with new token succeeds
    refresh_res_2 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert refresh_res_2.status_code == 200


async def test_logout_revokes_session(async_client: AsyncClient) -> None:
    """Test user logout revokes refresh token preventing subsequent refresh."""
    reg_payload = {
        "email": "helen@example.com",
        "password": "SecurePassword123!",
        "first_name": "Helen",
        "last_name": "Keller",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    refresh_token = reg_res.json()["tokens"]["refresh_token"]

    # Logout
    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"

    # Attempting to refresh with logged-out token must fail
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 401
    assert refresh_res.json()["error"]["code"] == "UNAUTHORIZED"


async def test_deactivated_user_login_and_access(
    async_client: AsyncClient,
    db_session,
) -> None:
    """Test that deactivated users cannot login or access protected routes."""
    from sqlalchemy import select

    from app.core.security import create_access_token
    from app.modules.users.models import User

    reg_payload = {
        "email": "inactive@example.com",
        "password": "SecurePassword123!",
        "first_name": "Inactive",
        "last_name": "User",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # Deactivate user in database
    stmt = select(User).where(User.email == "inactive@example.com")
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.is_active = False
    await db_session.commit()

    # Login fails with 403 Forbidden
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 403
    assert login_res.json()["error"]["code"] == "PERMISSION_DENIED"

    # Protected endpoint access fails with 403
    token = create_access_token(subject=user.id)
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 403
    assert me_res.json()["error"]["code"] == "PERMISSION_DENIED"


async def test_auth_token_nonexistent_user(
    async_client: AsyncClient,
) -> None:
    """Test accessing protected route with token of non-existent user."""
    import uuid

    from app.core.security import create_access_token

    fake_user_id = uuid.uuid4()
    token = create_access_token(subject=fake_user_id)
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 401
    assert me_res.json()["error"]["code"] == "UNAUTHORIZED"
