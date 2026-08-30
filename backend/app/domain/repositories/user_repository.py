from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def store_refresh_token(self, user_id: UUID, token_hash: str, expires_at) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_valid_refresh_token(self, token_hash: str):
        raise NotImplementedError

    @abstractmethod
    async def revoke_refresh_token(self, token_hash: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_refresh_tokens_for_user(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def mark_verified(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_password(self, user_id: UUID, hashed_password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        raise NotImplementedError
