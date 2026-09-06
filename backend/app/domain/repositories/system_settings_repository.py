from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.system_settings import SystemSettings


class SystemSettingsRepository(ABC):
    @abstractmethod
    async def get_settings(self) -> SystemSettings:
        raise NotImplementedError

    @abstractmethod
    async def update_settings(
        self, min_confidence_threshold: float, min_reward_risk_ratio: float, updated_by: UUID
    ) -> SystemSettings:
        raise NotImplementedError
