from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_user_repository
from app.application.dto.auth_dto import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.use_cases.authenticate_user import authenticate_user
from app.application.use_cases.logout_user import logout_user
from app.application.use_cases.refresh_token import refresh_access_token
from app.application.use_cases.register_user import register_user
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    return await register_user(payload, repository)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    return await authenticate_user(payload, repository)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    return await refresh_access_token(payload, repository)


@router.post("/logout", status_code=204)
async def logout(
    payload: RefreshRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> None:
    await logout_user(payload, repository)


@router.get("/me", response_model=UserResponse)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        permissions=current_user.permissions,
        is_active=current_user.is_active,
    )
