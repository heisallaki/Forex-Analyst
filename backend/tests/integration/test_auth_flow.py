import uuid


async def test_register_then_login_returns_consistent_user_shape(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "Test User", "role": "viewer"},
    )
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert "access_token" in register_body
    assert "refresh_token" in register_body
    assert register_body["user"]["is_verified"] is False

    login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123!"})
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["user"]["email"] == email
    assert "is_verified" in login_body["user"]


async def test_login_with_wrong_password_returns_401(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "Test User", "role": "viewer"},
    )
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
    assert response.status_code == 401


async def test_protected_endpoint_rejects_missing_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_endpoint_returns_authenticated_user(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "Test User", "role": "analyst"},
    )
    token = register_response.json()["access_token"]
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


async def test_refresh_token_rotates_and_invalidates_old_token(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "Test User", "role": "viewer"},
    )
    old_refresh_token = register_response.json()["refresh_token"]

    first_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})
    assert first_refresh.status_code == 200

    second_attempt = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})
    assert second_attempt.status_code == 401