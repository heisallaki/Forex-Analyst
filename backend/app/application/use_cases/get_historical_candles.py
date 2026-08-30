from app.application.dto.market_dto import CandleResponse
from app.domain.repositories.market_repository import MarketRepository
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


async def get_historical_candles(
    symbol: str,
    interval: str,
    limit: int,
    repository: MarketRepository,
    client: TwelveDataClient,
) -> list[CandleResponse]:
    stored = await repository.get_candles(symbol, interval, limit)

    if len(stored) < limit:
        fetched = await client.get_time_series(symbol, interval, limit)
        await repository.upsert_candles(fetched)
    else:
        refresh_window = min(limit, 5)
        recent = await client.get_time_series(symbol, interval, refresh_window)
        await repository.upsert_candles(recent)

    refreshed = await repository.get_candles(symbol, interval, limit)
    return [CandleResponse(**candle.__dict__) for candle in refreshed]
