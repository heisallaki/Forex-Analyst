from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.paper_trading_dto import (
    CloseTradeRequest,
    PartialCloseTradeRequest,
    TradeResponse,
)
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.repositories.market_repository import MarketRepository
from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.infrastructure.market_data.price_cache import get_latest_price
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


def _to_response(trade) -> TradeResponse:
    return TradeResponse(
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
        trailing_stop_distance=trade.trailing_stop_distance,
        margin_used=trade.margin_used,
        realized_pnl=trade.realized_pnl,
        status=trade.status,
        pnl=trade.pnl,
        opened_at=trade.opened_at,
        closed_at=trade.closed_at,
    )


async def _resolve_exit_price(
    symbol: str,
    exit_price: float | None,
    market_repository: MarketRepository,
    client: TwelveDataClient,
) -> float:
    if exit_price is not None:
        return exit_price
    latest = await get_latest_price(symbol)
    if latest is not None:
        return latest
    candles = await get_historical_candles(symbol, "1min", 1, market_repository, client)
    if not candles:
        raise ValueError(f"No price data available to close {symbol}")
    return candles[-1].close


async def close_paper_trade_use_case(
    trade_id: UUID,
    payload: CloseTradeRequest,
    repository: PaperTradingRepository,
    market_repository: MarketRepository,
    client: TwelveDataClient,
) -> TradeResponse:
    trade = await repository.get_trade(trade_id)
    if trade is None or trade.status != "open":
        raise ValueError("Trade not found or already closed")

    exit_price = await _resolve_exit_price(
        trade.symbol, payload.exit_price, market_repository, client
    )
    closed = await repository.close_trade(trade_id, exit_price, datetime.now(UTC))
    if closed is None:
        raise ValueError("Trade could not be closed")
    return _to_response(closed)


async def partial_close_paper_trade_use_case(
    trade_id: UUID,
    payload: PartialCloseTradeRequest,
    repository: PaperTradingRepository,
    market_repository: MarketRepository,
    client: TwelveDataClient,
) -> TradeResponse:
    trade = await repository.get_trade(trade_id)
    if trade is None or trade.status != "open":
        raise ValueError("Trade not found or already closed")
    if payload.quantity >= trade.quantity:
        raise ValueError(
            "Partial close quantity must be less than the open quantity; use full close instead"
        )

    exit_price = await _resolve_exit_price(trade.symbol, None, market_repository, client)
    updated = await repository.partial_close_trade(
        trade_id, payload.quantity, exit_price, datetime.now(UTC)
    )
    if updated is None:
        raise ValueError("Trade could not be partially closed")
    return _to_response(updated)
