from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.backtest_dto import SignalListItem
from app.application.dto.decision_dto import RecommendationResponse
from app.application.use_cases.generate_recommendation import generate_recommendation_use_case
from app.domain.entities.user import User
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.ai_prediction_repository_impl import (
    SqlAlchemyAIPredictionRepository,
)
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
            symbol, interval, market_repository, prediction_repository, backtest_repository, client
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/signals", response_model=list[SignalListItem])
async def signals(
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    symbol: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[SignalListItem]:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    signal_list = await backtest_repository.list_signals(symbol, limit)
    return [
        SignalListItem(
            id=str(signal.id),
            strategy_id=str(signal.strategy_id) if signal.strategy_id else None,
            symbol=signal.symbol,
            direction=signal.direction,
            confidence=signal.confidence,
            reasoning=signal.reasoning,
            created_at=signal.created_at,
        )
        for signal in signal_list
    ]
