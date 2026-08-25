from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.market import Candle, Tick
from app.domain.repositories.market_repository import MarketRepository
from app.infrastructure.database.models.candle_model import CandleModel
from app.infrastructure.database.models.tick_model import TickModel


def _to_entity(model: CandleModel) -> Candle:
    return Candle(
        symbol=model.symbol,
        interval=model.interval,
        open=model.open,
        high=model.high,
        low=model.low,
        close=model.close,
        volume=model.volume,
        timestamp=model.timestamp,
    )


class SqlAlchemyMarketRepository(MarketRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_candles(self, symbol: str, interval: str, limit: int) -> list[Candle]:
        result = await self.session.execute(
            select(CandleModel)
            .where(CandleModel.symbol == symbol, CandleModel.interval == interval)
            .order_by(CandleModel.timestamp.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [_to_entity(model) for model in reversed(models)]

    async def upsert_candles(self, candles: list[Candle]) -> int:
        if not candles:
            return 0
        values = [
            {
                "symbol": candle.symbol,
                "interval": candle.interval,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "timestamp": candle.timestamp,
            }
            for candle in candles
        ]
        stmt = insert(CandleModel).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_candle_symbol_interval_ts",
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return len(values)

    async def store_tick(self, tick: Tick) -> None:
        model = TickModel(symbol=tick.symbol, price=tick.price, timestamp=tick.timestamp)
        self.session.add(model)
        await self.session.commit()
