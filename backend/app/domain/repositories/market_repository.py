from abc import ABC, abstractmethod

from app.domain.entities.market import Candle


class MarketRepository(ABC):
    @abstractmethod
    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[Candle]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_candles(self, candles: list[Candle]) -> int:
        raise NotImplementedError
