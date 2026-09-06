from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.backtest import Metric, Signal, Strategy, Trade
from app.domain.repositories.backtest_repository import BacktestRepository
from app.infrastructure.database.models.metric_model import MetricModel
from app.infrastructure.database.models.signal_model import SignalModel
from app.infrastructure.database.models.strategy_model import StrategyModel
from app.infrastructure.database.models.trade_model import TradeModel


def _signal_to_entity(model: SignalModel) -> Signal:
    return Signal(
        id=model.id,
        strategy_id=model.strategy_id,
        symbol=model.symbol,
        direction=model.direction,
        confidence=model.confidence,
        reasoning=model.reasoning,
        created_at=model.created_at,
        user_id=model.user_id,
        hidden_at=model.hidden_at,
        outcome=model.outcome,
        evaluated_at=model.evaluated_at,
    )


def _strategy_to_entity(model: StrategyModel) -> Strategy:
    return Strategy(
        id=model.id,
        name=model.name,
        description=model.description,
        parameters=model.parameters,
        version=model.version,
        is_active=model.is_active,
    )


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
                name=name,
                description=description,
                parameters=parameters,
                version=1,
                is_active=False,
            )
            self.session.add(model)
        else:
            model.description = description
            model.parameters = parameters
            model.version += 1
        await self.session.commit()
        await self.session.refresh(model)
        return _strategy_to_entity(model)

    async def save_signal(self, signal: Signal) -> Signal:
        model = SignalModel(
            id=signal.id,
            strategy_id=signal.strategy_id,
            user_id=signal.user_id,
            symbol=signal.symbol,
            direction=signal.direction,
            confidence=signal.confidence,
            reasoning=signal.reasoning,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _signal_to_entity(model)

    async def save_trade(self, trade: Trade) -> Trade:
        model = TradeModel(
            id=trade.id,
            signal_id=trade.signal_id,
            portfolio_id=trade.portfolio_id,
            symbol=trade.symbol,
            side=trade.side,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            quantity=trade.quantity,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
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

    async def list_signals(
        self, symbol: str | None, limit: int, include_hidden: bool
    ) -> list[Signal]:
        query = select(SignalModel)
        if symbol is not None:
            query = query.where(SignalModel.symbol == symbol)
        if not include_hidden:
            query = query.where(SignalModel.hidden_at.is_(None))
        query = query.order_by(SignalModel.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return [_signal_to_entity(model) for model in result.scalars().all()]

    async def set_signals_hidden(
        self, signal_ids: list[UUID], hidden: bool, requesting_user_id: UUID, is_admin: bool
    ) -> tuple[list[UUID], list[UUID]]:
        result = await self.session.execute(
            select(SignalModel).where(SignalModel.id.in_(signal_ids))
        )
        models = result.scalars().all()
        succeeded: list[UUID] = []
        skipped: list[UUID] = []
        for model in models:
            owned = model.user_id is not None and model.user_id == requesting_user_id
            if is_admin or owned:
                model.hidden_at = datetime.now(UTC) if hidden else None
                succeeded.append(model.id)
            else:
                skipped.append(model.id)
        await self.session.commit()
        found_ids = {model.id for model in models}
        skipped.extend([signal_id for signal_id in signal_ids if signal_id not in found_ids])
        return succeeded, skipped

    async def delete_signals(
        self, signal_ids: list[UUID], requesting_user_id: UUID, is_admin: bool
    ) -> tuple[list[UUID], list[UUID]]:
        result = await self.session.execute(
            select(SignalModel).where(SignalModel.id.in_(signal_ids))
        )
        models = result.scalars().all()
        succeeded: list[UUID] = []
        skipped: list[UUID] = []
        for model in models:
            owned = model.user_id is not None and model.user_id == requesting_user_id
            if is_admin or owned:
                await self.session.delete(model)
                succeeded.append(model.id)
            else:
                skipped.append(model.id)
        await self.session.commit()
        found_ids = {model.id for model in models}
        skipped.extend([signal_id for signal_id in signal_ids if signal_id not in found_ids])
        return succeeded, skipped

    async def list_strategies(self) -> list[Strategy]:
        result = await self.session.execute(
            select(StrategyModel).order_by(StrategyModel.created_at.desc())
        )
        return [_strategy_to_entity(model) for model in result.scalars().all()]

    async def activate_strategy(self, strategy_id: UUID) -> None:
        result = await self.session.execute(
            select(StrategyModel).where(StrategyModel.id == strategy_id)
        )
        model = result.scalar_one_or_none()
        if model is not None and not model.is_active:
            model.is_active = True
            await self.session.commit()

    async def list_signals_for_evaluation(self, limit: int) -> list[Signal]:
        query = (
            select(SignalModel)
            .where(
                SignalModel.direction.in_(["long", "short"]),
                SignalModel.outcome.is_(None),
                SignalModel.reasoning["source"].astext == "decision_engine",
            )
            .order_by(SignalModel.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [_signal_to_entity(model) for model in result.scalars().all()]

    async def record_signal_outcome(self, signal_id: UUID, outcome: str) -> None:
        result = await self.session.execute(select(SignalModel).where(SignalModel.id == signal_id))
        model = result.scalar_one_or_none()
        if model is not None:
            model.outcome = outcome
            model.evaluated_at = datetime.now(UTC)
            await self.session.commit()

    async def get_accuracy_stats(self) -> dict:
        result = await self.session.execute(
            select(SignalModel).where(SignalModel.outcome.isnot(None))
        )
        evaluated = result.scalars().all()

        wins = sum(1 for signal in evaluated if signal.outcome == "win")
        losses = sum(1 for signal in evaluated if signal.outcome == "loss")
        flats = sum(1 for signal in evaluated if signal.outcome == "flat")
        total = len(evaluated)

        long_signals = [signal for signal in evaluated if signal.direction == "long"]
        short_signals = [signal for signal in evaluated if signal.direction == "short"]
        long_decided = [signal for signal in long_signals if signal.outcome in ("win", "loss")]
        short_decided = [signal for signal in short_signals if signal.outcome in ("win", "loss")]
        decided = wins + losses

        return {
            "total_evaluated": total,
            "wins": wins,
            "losses": losses,
            "flats": flats,
            "win_rate": (wins / decided * 100) if decided > 0 else None,
            "long_win_rate": (
                sum(1 for signal in long_decided if signal.outcome == "win")
                / len(long_decided)
                * 100
                if long_decided
                else None
            ),
            "short_win_rate": (
                sum(1 for signal in short_decided if signal.outcome == "win")
                / len(short_decided)
                * 100
                if short_decided
                else None
            ),
        }
