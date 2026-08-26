from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.backtest_dto import BacktestRunRequest, BacktestRunResponse
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
