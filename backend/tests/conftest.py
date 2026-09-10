import os
import uuid
from datetime import UTC, datetime

from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://forex_dev:changeme@localhost:5432/forex_analyst_test",
    ),
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production-use")
os.environ.setdefault("TWELVE_DATA_API_KEY", "test-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SMTP_HOST", "")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_db_session
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (  # noqa: F401
    ai_prediction_model,
    candle_model,
    log_model,
    metric_model,
    portfolio_model,
    refresh_token_model,
    signal_model,
    strategy_model,
    system_settings_model,
    tick_model,
    trade_model,
    trained_model_model,
    user_model,
    verification_code_model,
)
from app.main import app, fastapi_app

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email=f"test-{uuid.uuid4()}@example.com",
        hashed_password="test-hashed-password",
        full_name="Test User",
        role="viewer",
        permissions=User.default_permissions_for_role("viewer"),
        is_active=True,
        is_verified=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    repository = SqlAlchemyUserRepository(db_session)
    return await repository.create(user)


@pytest_asyncio.fixture
async def client():
    async def override_get_db_session():
        async with TestSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
    fastapi_app.state.limiter.enabled = False

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    fastapi_app.state.limiter.enabled = True
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def rate_limited_client():
    async def override_get_db_session():
        async with TestSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db_session] = override_get_db_session
    fastapi_app.state.limiter.enabled = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    fastapi_app.dependency_overrides.clear()