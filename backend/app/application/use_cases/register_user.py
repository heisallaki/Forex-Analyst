from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status

from app.application.dto.auth_dto import RegisterRequest, TokenResponse, UserResponse
from app.core.security import (
    create_access_token,
    generate_refresh_token_value,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
)
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


async def register_user(payload: RegisterRequest, repository: UserRepository) -> TokenResponse:
    existing = await repository.get_by_email(payload.email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    now = datetime.now(UTC)
    user = User(
        id=uuid4(),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        permissions=User.default_permissions_for_role(payload.role),
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    created = await repository.create(user)

    access_token = create_access_token(str(created.id), created.role, created.permissions)
    raw_refresh = generate_refresh_token_value()
    await repository.store_refresh_token(
        created.id, hash_refresh_token(raw_refresh), refresh_token_expiry()
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserResponse(
            id=str(created.id),
            email=created.email,
            full_name=created.full_name,
            role=created.role,
            permissions=created.permissions,
            is_active=created.is_active,
        ),
    )
