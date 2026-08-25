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
