from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.backtest import Metric, Signal, Strategy, Trade
from app.domain.repositories.backtest_repository import BacktestRepository
from app.infrastructure.database.models.metric_model import MetricModel
from app.infrastructure.database.models.signal_model import SignalModel
from app.infrastructure.database.models.strategy_model import StrategyModel
from app.infrastructure.database.models.trade_model import TradeModel


class SqlAlchemyBacktestRepository(BacktestRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_strategy(
        self, name: str, description: str | None, parameters: dict
    ) -> Strategy:
        result = await self.session.execute(select(StrategyModel).where(StrategyModel.name == name))
        model = result.scalar_one_or_none()
        if model is None:
            model = StrategyModel(
                name=name, description=description, parameters=parameters, is_active=False
            )
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
        return Strategy(
            id=model.id,
            name=model.name,
            description=model.description,
            parameters=model.parameters,
            is_active=model.is_active,
        )

    async def save_signal(self, signal: Signal) -> Signal:
        model = SignalModel(
            id=signal.id,
            strategy_id=signal.strategy_id,
            symbol=signal.symbol,
            direction=signal.direction,
            confidence=signal.confidence,
            reasoning=signal.reasoning,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return Signal(
            id=model.id,
            strategy_id=model.strategy_id,
            symbol=model.symbol,
            direction=model.direction,
            confidence=model.confidence,
            reasoning=model.reasoning,
            created_at=model.created_at,
        )

    async def save_trade(self, trade: Trade) -> Trade:
        model = TradeModel(
            id=trade.id,
            signal_id=trade.signal_id,
            symbol=trade.symbol,
            side=trade.side,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            quantity=trade.quantity,
            status=trade.status,
            is_paper=trade.is_paper,
            pnl=trade.pnl,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return trade

    async def save_metrics(self, metrics: list[Metric]) -> int:
        if not metrics:
            return 0
        models = [
            MetricModel(id=metric.id, name=metric.name, value=metric.value, tags=metric.tags)
            for metric in metrics
        ]
        self.session.add_all(models)
        await self.session.commit()
        return len(models)
