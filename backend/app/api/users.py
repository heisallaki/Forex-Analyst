from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.user_management_dto import (
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserListItem,
)
from app.application.use_cases.manage_users import (
    list_users_use_case,
    update_user_role_use_case,
    update_user_status_use_case,
)
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserListItem])
async def list_users(
    current_user: Annotated[User, Depends(require_permission("manage_users"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[UserListItem]:
    repository = SqlAlchemyUserRepository(session)
    return await list_users_use_case(repository)


@router.patch("/{user_id}/role", response_model=UserListItem)
async def update_user_role(
    user_id: UUID,
    payload: UpdateUserRoleRequest,
    current_user: Annotated[User, Depends(require_permission("manage_users"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserListItem:
    repository = SqlAlchemyUserRepository(session)
    return await update_user_role_use_case(user_id, payload.role, repository)


@router.patch("/{user_id}/status", response_model=UserListItem)
async def update_user_status(
    user_id: UUID,
    payload: UpdateUserStatusRequest,
    current_user: Annotated[User, Depends(require_permission("manage_users"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserListItem:
    repository = SqlAlchemyUserRepository(session)
    return await update_user_status_use_case(
        user_id, payload.is_active, current_user.id, repository
    )
