from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_admin
from app.application.dto.execution_dto import (
    ExecutionResultResponse,
    ExecutionStatusResponse,
    SubmitOrderRequest,
)
from app.application.use_cases.submit_execution_order import submit_execution_order_use_case
from app.core.config import settings
from app.domain.entities.user import User
from app.infrastructure.repositories.execution_repository_impl import (
    SqlAlchemyExecutionAuditRepository,
)

router = APIRouter(prefix="/execution", tags=["execution"])


@router.get("/status", response_model=ExecutionStatusResponse)
async def execution_status(
    current_user: Annotated[User, Depends(require_admin())],
) -> ExecutionStatusResponse:
    return ExecutionStatusResponse(
        execution_enabled=settings.EXECUTION_ENABLED,
        max_position_size=settings.EXECUTION_MAX_POSITION_SIZE,
        max_open_positions=settings.EXECUTION_MAX_OPEN_POSITIONS,
        max_daily_loss_pct=settings.EXECUTION_MAX_DAILY_LOSS_PCT,
        broker_configured=False,
    )


@router.post("/orders", response_model=ExecutionResultResponse)
async def submit_order(
    payload: SubmitOrderRequest,
    current_user: Annotated[User, Depends(require_admin())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExecutionResultResponse:
    audit_repository = SqlAlchemyExecutionAuditRepository(session)
    return await submit_execution_order_use_case(payload, audit_repository)
