from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.paper_trading_dto import OpenTradeRequest, TradeResponse
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.entities.paper_trading import PaperTrade
from app.domain.repositories.market_repository import MarketRepository
from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.infrastructure.market_data.price_cache import get_latest_price
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


async def _resolve_entry_price(
    symbol: str, market_repository: MarketRepository, client: TwelveDataClient
) -> float:
    latest = await get_latest_price(symbol)
    if latest is not None:
        return latest
    candles = await get_historical_candles(symbol, "1min", 1, market_repository, client)
    if not candles:
        raise ValueError(f"No price data available for {symbol}")
    return candles[-1].close


async def open_paper_trade_use_case(
    payload: OpenTradeRequest,
    user_id: UUID,
    repository: PaperTradingRepository,
    market_repository: MarketRepository,
    client: TwelveDataClient,
) -> TradeResponse:
    portfolio = await repository.get_portfolio(UUID(payload.portfolio_id), user_id)
    if portfolio is None:
        raise ValueError("Portfolio not found")

    entry_price = await _resolve_entry_price(payload.symbol, market_repository, client)

    quantity = payload.quantity
    if quantity is None:
        if payload.risk_amount is None or payload.stop_loss is None:
            raise ValueError(
                "Provide either quantity, or both risk_amount and stop_loss for risk-based sizing"
            )
        stop_distance = abs(entry_price - payload.stop_loss)
        if stop_distance <= 0:
            raise ValueError("stop_loss must differ from the current market price")
        quantity = payload.risk_amount / stop_distance

    trade = PaperTrade(
        id=uuid4(),
        portfolio_id=portfolio.id,
        signal_id=UUID(payload.signal_id) if payload.signal_id else None,
        symbol=payload.symbol,
        side=payload.side,
        entry_price=entry_price,
        exit_price=None,
        quantity=quantity,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        status="open",
        pnl=None,
        opened_at=datetime.now(UTC),
        closed_at=None,
    )
    opened = await repository.open_trade(trade)
    return TradeResponse(
        id=str(opened.id),
        portfolio_id=str(opened.portfolio_id),
        signal_id=str(opened.signal_id) if opened.signal_id else None,
        symbol=opened.symbol,
        side=opened.side,
        entry_price=opened.entry_price,
        exit_price=opened.exit_price,
        quantity=opened.quantity,
        stop_loss=opened.stop_loss,
        take_profit=opened.take_profit,
        status=opened.status,
        pnl=opened.pnl,
        opened_at=opened.opened_at,
        closed_at=opened.closed_at,
    )
