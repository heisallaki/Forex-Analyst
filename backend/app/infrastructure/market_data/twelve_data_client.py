from datetime import UTC, datetime

import httpx

from app.core.config import settings
from app.domain.entities.market import Candle


class TwelveDataClient:
    def __init__(self) -> None:
        self.base_url = settings.TWELVE_DATA_REST_URL
        self.api_key = settings.TWELVE_DATA_API_KEY

    async def get_time_series(self, symbol: str, interval: str, output_size: int) -> list[Candle]:
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": str(output_size),
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{self.base_url}/time_series", params=params)
            response.raise_for_status()
            payload = response.json()

        if payload.get("status") == "error":
            raise RuntimeError(payload.get("message", "Twelve Data request failed"))

        candles: list[Candle] = []
        for row in payload.get("values", []):
            candles.append(
                Candle(
                    symbol=symbol,
                    interval=interval,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]) if row.get("volume") not in (None, "") else None,
                    timestamp=datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").replace(
                        tzinfo=UTC
                    )
                    if len(row["datetime"]) > 10
                    else datetime.strptime(row["datetime"], "%Y-%m-%d").replace(tzinfo=UTC),
                )
            )
        return candles
