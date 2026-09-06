from uuid import UUID

from fastapi import HTTPException, status

from app.application.dto.user_management_dto import UserListItem
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


def _to_list_item(user: User) -> UserListItem:
    return UserListItem(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


async def list_users_use_case(repository: UserRepository) -> list[UserListItem]:
    users = await repository.list_all()
    return [_to_list_item(user) for user in users]


async def update_user_role_use_case(
    user_id: UUID, role: str, repository: UserRepository
) -> UserListItem:
    target = await repository.get_by_id(user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    permissions = User.default_permissions_for_role(role)
    await repository.update_role(user_id, role, permissions)
    updated = await repository.get_by_id(user_id)
    return _to_list_item(updated)


async def update_user_status_use_case(
    user_id: UUID, is_active: bool, requesting_user_id: UUID, repository: UserRepository
) -> UserListItem:
    if user_id == requesting_user_id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account"
        )
    target = await repository.get_by_id(user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await repository.set_active(user_id, is_active)
    updated = await repository.get_by_id(user_id)
    return _to_list_item(updated)
