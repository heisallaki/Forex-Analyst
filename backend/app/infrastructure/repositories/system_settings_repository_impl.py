from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.system_settings import SystemSettings
from app.domain.repositories.system_settings_repository import SystemSettingsRepository
from app.infrastructure.database.models.system_settings_model import SystemSettingsModel


def _to_entity(model: SystemSettingsModel) -> SystemSettings:
    return SystemSettings(
        id=model.id,
        min_confidence_threshold=model.min_confidence_threshold,
        min_reward_risk_ratio=model.min_reward_risk_ratio,
        updated_at=model.updated_at,
        updated_by=model.updated_by,
    )


class SqlAlchemySystemSettingsRepository(SystemSettingsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self) -> SystemSettings:
        result = await self.session.execute(select(SystemSettingsModel).limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            model = SystemSettingsModel(id=uuid4())
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
        return _to_entity(model)

    async def update_settings(
        self, min_confidence_threshold: float, min_reward_risk_ratio: float, updated_by: UUID
    ) -> SystemSettings:
        result = await self.session.execute(select(SystemSettingsModel).limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            model = SystemSettingsModel(id=uuid4())
            self.session.add(model)
        model.min_confidence_threshold = min_confidence_threshold
        model.min_reward_risk_ratio = min_reward_risk_ratio
        model.updated_by = updated_by
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)
