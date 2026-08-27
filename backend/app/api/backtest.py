from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.backtest_dto import (
    BacktestRunRequest,
    BacktestRunResponse,
    StrategyListItem,
)
from app.application.use_cases.run_backtest import run_backtest_use_case
from app.domain.entities.user import User
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.backtest_repository_impl import SqlAlchemyBacktestRepository
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.post("/run", response_model=BacktestRunResponse)
async def run_backtest_endpoint(
    payload: BacktestRunRequest,
    current_user: Annotated[User, Depends(require_permission("manage_strategies"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BacktestRunResponse:
    market_repository = SqlAlchemyMarketRepository(session)
    backtest_repository = SqlAlchemyBacktestRepository(session)
    client = TwelveDataClient()
    return await run_backtest_use_case(payload, market_repository, backtest_repository, client)


@router.get("/strategies", response_model=list[StrategyListItem])
async def strategies(
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[StrategyListItem]:
    backtest_repository = SqlAlchemyBacktestRepository(session)
    strategy_list = await backtest_repository.list_strategies()
    return [
        StrategyListItem(
            id=str(item.id), name=item.name, description=item.description, is_active=item.is_active
        )
        for item in strategy_list
    ]
