from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.domain.entities.user import User
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await repository.get_by_id(UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_permission(permission: str):
    async def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not current_user.permissions.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return checker
