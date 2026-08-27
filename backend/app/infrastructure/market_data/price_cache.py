from app.infrastructure.cache.redis_client import get_redis_client

LATEST_PRICE_KEY_PREFIX = "market:latest:"


async def get_latest_price(symbol: str) -> float | None:
    redis_client = get_redis_client()
    value = await redis_client.get(f"{LATEST_PRICE_KEY_PREFIX}{symbol}")
    if value is None:
        return None
    return float(value)
