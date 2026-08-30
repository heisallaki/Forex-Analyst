from fastapi import HTTPException, status

from app.application.dto.auth_dto import LoginRequest, TokenResponse, UserResponse
from app.core.security import (
    create_access_token,
    generate_refresh_token_value,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.domain.repositories.user_repository import UserRepository


async def authenticate_user(payload: LoginRequest, repository: UserRepository) -> TokenResponse:
    user = await repository.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    access_token = create_access_token(str(user.id), user.role, user.permissions)
    raw_refresh = generate_refresh_token_value()
    await repository.store_refresh_token(
        user.id, hash_refresh_token(raw_refresh), refresh_token_expiry()
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            permissions=user.permissions,
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
    )
