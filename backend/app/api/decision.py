from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.backtest_dto import SignalBulkActionRequest, SignalBulkActionResponse, SignalListItem
from app.application.dto.decision_dto import RecommendationResponse
from app.application.use_cases.generate_recommendation import generate_recommendation_use_case
from app.domain.entities.user import User
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.ai_prediction_repository_impl import SqlAlchemyAIPredictionRepository
from app.infrastructure.repositories.backtest_repository_impl import SqlAlchemyBacktestRepository
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

router = APIRouter(prefix="/decision", tags=["decision"])


@router.get("/recommend/{symbol:path}", response_model=RecommendationResponse)
async def recommend(
    symbol: str,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    interval: str = Query(default="1min"),
) -> RecommendationResponse:
    market_repository = SqlAlchemyMarketRepository(session)
    prediction_repository = SqlAlchemyAIPredictionRepository(session)
    backtest_repository = SqlAlchemyBacktestRepository(session)
    client = TwelveDataClient()
    try:
        return await generate_recommendation_use_case(
            symbol, interval, market_repository, prediction_repository, backtest_repository, client, current_user.id
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/signals", response_model=list[SignalListItem])
async def signals(
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    symbol: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    include_hidden: bool = Query(default=False),
) -> list[SignalListItem]:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    signal_list = await backtest_repository.list_signals(symbol, limit, include_hidden)
    return [
        SignalListItem(
            id=str(signal.id),
            strategy_id=str(signal.strategy_id) if signal.strategy_id else None,
            symbol=signal.symbol,
            direction=signal.direction,
            confidence=signal.confidence,
            reasoning=signal.reasoning,
            created_at=signal.created_at,
            hidden_at=signal.hidden_at,
            is_owner=signal.user_id is not None and signal.user_id == current_user.id,
        )
        for signal in signal_list
    ]


@router.post("/signals/hide", response_model=SignalBulkActionResponse)
async def hide_signals(
    payload: SignalBulkActionRequest,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SignalBulkActionResponse:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    ids = [UUID(value) for value in payload.signal_ids]
    succeeded, skipped = await backtest_repository.set_signals_hidden(
        ids, True, current_user.id, current_user.role == "admin"
    )
    return SignalBulkActionResponse(succeeded=[str(i) for i in succeeded], skipped=[str(i) for i in skipped])


@router.post("/signals/unhide", response_model=SignalBulkActionResponse)
async def unhide_signals(
    payload: SignalBulkActionRequest,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SignalBulkActionResponse:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    ids = [UUID(value) for value in payload.signal_ids]
    succeeded, skipped = await backtest_repository.set_signals_hidden(
        ids, False, current_user.id, current_user.role == "admin"
    )
    return SignalBulkActionResponse(succeeded=[str(i) for i in succeeded], skipped=[str(i) for i in skipped])


@router.post("/signals/delete", response_model=SignalBulkActionResponse)
async def delete_signals(
    payload: SignalBulkActionRequest,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SignalBulkActionResponse:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    ids = [UUID(value) for value in payload.signal_ids]
    succeeded, skipped = await backtest_repository.delete_signals(ids, current_user.id, current_user.role == "admin")
    return SignalBulkActionResponse(succeeded=[str(i) for i in succeeded], skipped=[str(i) for i in skipped])