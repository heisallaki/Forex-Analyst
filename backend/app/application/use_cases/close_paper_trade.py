from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.paper_trading_dto import CloseTradeRequest, TradeResponse
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.repositories.market_repository import MarketRepository
from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.infrastructure.market_data.price_cache import get_latest_price
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


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

    exit_price = payload.exit_price
    if exit_price is None:
        exit_price = await get_latest_price(trade.symbol)
        if exit_price is None:
            candles = await get_historical_candles(
                trade.symbol, "1min", 1, market_repository, client
            )
            if not candles:
                raise ValueError(f"No price data available to close {trade.symbol}")
            exit_price = candles[-1].close

    closed = await repository.close_trade(trade_id, exit_price, datetime.now(UTC))
    if closed is None:
        raise ValueError("Trade could not be closed")

    return TradeResponse(
        id=str(closed.id),
        portfolio_id=str(closed.portfolio_id),
        signal_id=str(closed.signal_id) if closed.signal_id else None,
        symbol=closed.symbol,
        side=closed.side,
        entry_price=closed.entry_price,
        exit_price=closed.exit_price,
        quantity=closed.quantity,
        stop_loss=closed.stop_loss,
        take_profit=closed.take_profit,
        status=closed.status,
        pnl=closed.pnl,
        opened_at=closed.opened_at,
        closed_at=closed.closed_at,
    )
