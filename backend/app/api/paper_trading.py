from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission, require_verified
from app.application.dto.paper_trading_dto import (
    CloseTradeRequest,
    CreatePortfolioRequest,
    OpenTradeRequest,
    PortfolioPerformanceResponse,
    PortfolioResponse,
    TradeResponse,
)
from app.application.use_cases.close_paper_trade import close_paper_trade_use_case
from app.application.use_cases.create_portfolio import create_portfolio_use_case
from app.application.use_cases.open_paper_trade import open_paper_trade_use_case
from app.domain.entities.user import User
from app.domain.services.portfolio_performance import compute_portfolio_performance
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository
from app.infrastructure.repositories.paper_trading_repository_impl import (
    SqlAlchemyPaperTradingRepository,
)

router = APIRouter(prefix="/paper", tags=["paper-trading"])


@router.post("/portfolios", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(
    payload: CreatePortfolioRequest,
    current_user: Annotated[User, Depends(require_permission("manage_strategies"))],
    verified_user: Annotated[User, Depends(require_verified())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PortfolioResponse:
    repository = SqlAlchemyPaperTradingRepository(session)
    return await create_portfolio_use_case(payload, current_user.id, repository)


@router.get("/portfolios", response_model=list[PortfolioResponse])
async def list_portfolios(
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[PortfolioResponse]:
    repository = SqlAlchemyPaperTradingRepository(session)
    portfolios = await repository.list_portfolios(current_user.id)
    return [
        PortfolioResponse(
            id=str(portfolio.id),
            name=portfolio.name,
            base_currency=portfolio.base_currency,
            initial_balance=portfolio.initial_balance,
            current_balance=portfolio.current_balance,
            created_at=portfolio.created_at,
        )
        for portfolio in portfolios
    ]


@router.get("/portfolios/{portfolio_id}/performance", response_model=PortfolioPerformanceResponse)
async def portfolio_performance(
    portfolio_id: UUID,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PortfolioPerformanceResponse:
    repository = SqlAlchemyPaperTradingRepository(session)
    portfolio = await repository.get_portfolio(portfolio_id, current_user.id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    trades = await repository.list_trades(portfolio_id, status=None)
    stats = compute_portfolio_performance(portfolio, trades)
    return PortfolioPerformanceResponse(**stats)


@router.post("/trades", response_model=TradeResponse, status_code=201)
async def open_trade(
    payload: OpenTradeRequest,
    current_user: Annotated[User, Depends(require_permission("manage_strategies"))],
    verified_user: Annotated[User, Depends(require_verified())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TradeResponse:
    repository = SqlAlchemyPaperTradingRepository(session)
    market_repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    try:
        return await open_paper_trade_use_case(
            payload, current_user.id, repository, market_repository, client
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/trades/{trade_id}/close", response_model=TradeResponse)
async def close_trade(
    trade_id: UUID,
    payload: CloseTradeRequest,
    current_user: Annotated[User, Depends(require_permission("manage_strategies"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TradeResponse:
    repository = SqlAlchemyPaperTradingRepository(session)
    market_repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    try:
        return await close_paper_trade_use_case(
            trade_id, payload, repository, market_repository, client
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/trades", response_model=list[TradeResponse])
async def list_trades(
    portfolio_id: UUID,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    trade_status: str | None = Query(default=None, alias="status"),
) -> list[TradeResponse]:
    repository = SqlAlchemyPaperTradingRepository(session)
    portfolio = await repository.get_portfolio(portfolio_id, current_user.id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    trades = await repository.list_trades(portfolio_id, trade_status)
    return [
        TradeResponse(
            id=str(trade.id),
            portfolio_id=str(trade.portfolio_id),
            signal_id=str(trade.signal_id) if trade.signal_id else None,
            symbol=trade.symbol,
            side=trade.side,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            quantity=trade.quantity,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            status=trade.status,
            pnl=trade.pnl,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
        )
        for trade in trades
    ]
