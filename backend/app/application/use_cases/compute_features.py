from app.application.dto.feature_dto import FeatureRow
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.entities.market import Candle
from app.domain.repositories.market_repository import MarketRepository
from app.domain.services.feature_engine import compute_feature_rows
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


async def compute_features(
    symbol: str,
    interval: str,
    limit: int,
    repository: MarketRepository,
    client: TwelveDataClient,
) -> list[FeatureRow]:
    candle_responses = await get_historical_candles(symbol, interval, limit, repository, client)
    candles = [
        Candle(
            symbol=symbol,
            interval=interval,
            open=item.open,
            high=item.high,
            low=item.low,
            close=item.close,
            volume=item.volume,
            timestamp=item.timestamp,
        )
        for item in candle_responses
    ]
    rows = compute_feature_rows(candles)
    return [FeatureRow(**row) for row in rows]
