import asyncio
import json
import logging
import ssl

import certifi
import websockets

from app.core.config import settings
from app.infrastructure.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)

MARKET_TICKS_CHANNEL = "market:ticks"


def _build_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=certifi.where())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


async def run_market_stream() -> None:
    url = f"{settings.TWELVE_DATA_WS_URL}?apikey={settings.TWELVE_DATA_API_KEY}"
    redis_client = get_redis_client()
    symbols = ",".join(settings.MARKET_INSTRUMENTS)
    ssl_context = _build_ssl_context()

    while True:
        try:
            async with websockets.connect(url, ssl=ssl_context) as connection:
                await connection.send(
                    json.dumps({"action": "subscribe", "params": {"symbols": symbols}})
                )
                async for message in connection:
                    try:
                        payload = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                    if payload.get("event") == "price":
                        await redis_client.publish(MARKET_TICKS_CHANNEL, json.dumps(payload))
        except asyncio.CancelledError:
            raise
        except Exception as error:
            logger.warning("Market stream disconnected, retrying: %s", error)
            await asyncio.sleep(5)