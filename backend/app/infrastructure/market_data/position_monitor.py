import asyncio
import json
import logging

from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.market_data.twelve_data_stream import MARKET_TICKS_CHANNEL
from app.infrastructure.repositories.paper_trading_repository_impl import (
    SqlAlchemyPaperTradingRepository,
)

logger = logging.getLogger(__name__)


async def _handle_tick(payload: dict) -> None:
    try:
        symbol = payload.get("symbol")
        price = payload.get("price")
        if symbol is None or price is None:
            return
        price_value = float(price)
        async with AsyncSessionLocal() as session:
            repository = SqlAlchemyPaperTradingRepository(session)
            open_trades = await repository.get_open_trades_for_symbol(symbol)
            for trade in open_trades:
                await repository.evaluate_and_close_if_triggered(trade, price_value)
    except Exception as error:
        logger.warning("Position monitor failed to process tick: %s", error)


async def run_position_monitor() -> None:
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(MARKET_TICKS_CHANNEL)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                try:
                    payload = json.loads(message["data"])
                except json.JSONDecodeError:
                    payload = None
                if payload is not None:
                    await _handle_tick(payload)
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(MARKET_TICKS_CHANNEL)
        await pubsub.close()
        raise
    except Exception as error:
        logger.warning("Position monitor loop error: %s", error)
