from app.application.dto.market_dto import BackfillRequest, BackfillResponse
from app.domain.repositories.market_repository import MarketRepository
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


async def backfill_candles(
    payload: BackfillRequest,
    repository: MarketRepository,
    client: TwelveDataClient,
) -> BackfillResponse:
    candles = await client.get_time_series(payload.symbol, payload.interval, payload.output_size)
    stored = await repository.upsert_candles(candles)
    return BackfillResponse(symbol=payload.symbol, interval=payload.interval, stored=stored)
