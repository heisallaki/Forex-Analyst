import asyncio
import json
import logging
import ssl
from datetime import datetime, timezone

import certifi
import websockets

from app.core.config import settings
from app.core.system_state import record_tick
from app.domain.entities.market import Tick
from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.market_data.price_cache import LATEST_PRICE_KEY_PREFIX
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

logger = logging.getLogger(__name__)

MARKET_TICKS_CHANNEL = "market:ticks"


def _build_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=certifi.where())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


async def _persist_tick(payload: dict) -> None:
    try:
        symbol = payload.get("symbol")
        price = payload.get("price")
        raw_timestamp = payload.get("timestamp")
        if symbol is None or price is None or raw_timestamp is None:
            return
        tick = Tick(
            symbol=symbol,
            price=float(price),
            timestamp=datetime.fromtimestamp(int(raw_timestamp), tz=timezone.utc),
        )
        async with AsyncSessionLocal() as session:
            repository = SqlAlchemyMarketRepository(session)
            await repository.store_tick(tick)
    except Exception as error:
        logger.warning("Failed to persist tick: %s", error)


async def run_market_stream() -> None:
    url = f"{settings.TWELVE_DATA_WS_URL}?apikey={settings.TWELVE_DATA_API_KEY}"
    redis_client = get_redis_client()
    symbols = ",".join(settings.MARKET_INSTRUMENTS)
    ssl_context = _build_ssl_context()

    while True:
        try:
            async with websockets.connect(url, ssl=ssl_context) as connection:
                logger.info("Market stream connected to Twelve Data")
                await connection.send(
                    json.dumps({"action": "subscribe", "params": {"symbols": symbols}})
                )
                async for message in connection:
                    try:
                        payload = json.loads(message)
                    except json.JSONDecodeError:
                        continue

                    event = payload.get("event")

                    if event == "subscribe-status":
                        if payload.get("status") == "error":
                            logger.error("Twelve Data rejected subscription: %s", payload)
                        else:
                            logger.info(
                                "Twelve Data subscription status: %s | success=%s fails=%s",
                                payload.get("status"),
                                payload.get("success"),
                                payload.get("fails"),
                            )
                        continue

                    if event == "price":
                        record_tick()
                        await redis_client.publish(MARKET_TICKS_CHANNEL, json.dumps(payload))
                        symbol = payload.get("symbol")
                        price = payload.get("price")
                        if symbol and price is not None:
                            await redis_client.set(f"{LATEST_PRICE_KEY_PREFIX}{symbol}", str(price))
                        asyncio.create_task(_persist_tick(payload))
        except asyncio.CancelledError:
            raise
        except Exception as error:
            logger.warning("Market stream disconnected, retrying: %s", error)
            await asyncio.sleep(5)