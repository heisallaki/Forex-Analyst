from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_admin
from app.application.dto.admin_settings_dto import (
    SystemSettingsResponse,
    UpdateSystemSettingsRequest,
)
from app.domain.entities.user import User
from app.infrastructure.repositories.system_settings_repository_impl import (
    SqlAlchemySystemSettingsRepository,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    current_user: Annotated[User, Depends(require_admin())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SystemSettingsResponse:
    repository = SqlAlchemySystemSettingsRepository(session)
    settings = await repository.get_settings()
    return SystemSettingsResponse(
        min_confidence_threshold=settings.min_confidence_threshold,
        min_reward_risk_ratio=settings.min_reward_risk_ratio,
        updated_at=settings.updated_at,
        updated_by=str(settings.updated_by) if settings.updated_by else None,
    )


@router.patch("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    payload: UpdateSystemSettingsRequest,
    current_user: Annotated[User, Depends(require_admin())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SystemSettingsResponse:
    repository = SqlAlchemySystemSettingsRepository(session)
    settings = await repository.update_settings(
        payload.min_confidence_threshold, payload.min_reward_risk_ratio, current_user.id
    )
    return SystemSettingsResponse(
        min_confidence_threshold=settings.min_confidence_threshold,
        min_reward_risk_ratio=settings.min_reward_risk_ratio,
        updated_at=settings.updated_at,
        updated_by=str(settings.updated_by) if settings.updated_by else None,
    )
