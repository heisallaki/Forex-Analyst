import pytest_asyncio

from app.core.rate_limit import limiter


@pytest_asyncio.fixture
async def clean_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


async def test_login_endpoint_returns_429_after_exceeding_limit(
    rate_limited_client,
    clean_rate_limiter,
):
    email = "rate-limit-test@example.com"
    payload = {"email": email, "password": "WrongPassword"}

    responses = [
        await rate_limited_client.post(
            "/api/v1/auth/login",
            json=payload,
        )
        for _ in range(11)
    ]

    assert any(response.status_code == 429 for response in responses)
    assert responses[0].status_code != 429
