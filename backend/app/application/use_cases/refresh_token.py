from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.application.dto.auth_dto import RefreshRequest, TokenResponse, UserResponse
from app.core.security import (
    create_access_token,
    generate_refresh_token_value,
    hash_refresh_token,
    refresh_token_expiry,
)
from app.domain.repositories.user_repository import UserRepository


async def refresh_access_token(
    payload: RefreshRequest, repository: UserRepository
) -> TokenResponse:
    token_hash = hash_refresh_token(payload.refresh_token)
    stored = await repository.get_valid_refresh_token(token_hash)
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    if stored.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    user = await repository.get_by_id(stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
        )

    await repository.revoke_refresh_token(token_hash)

    access_token = create_access_token(str(user.id), user.role, user.permissions)
    new_raw_refresh = generate_refresh_token_value()
    await repository.store_refresh_token(
        user.id, hash_refresh_token(new_raw_refresh), refresh_token_expiry()
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw_refresh,
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
