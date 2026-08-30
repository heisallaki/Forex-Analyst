from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.verification import VerificationCode


class VerificationRepository(ABC):
    @abstractmethod
    async def create_code(
        self, user_id: UUID, purpose: str, code_hash: str, expires_at: datetime
    ) -> VerificationCode:
        raise NotImplementedError

    @abstractmethod
    async def get_latest_active_code(self, user_id: UUID, purpose: str) -> VerificationCode | None:
        raise NotImplementedError

    @abstractmethod
    async def get_valid_code(
        self, user_id: UUID, purpose: str, code_hash: str
    ) -> VerificationCode | None:
        raise NotImplementedError

    @abstractmethod
    async def consume_code(self, code_id: UUID) -> None:
        raise NotImplementedError
