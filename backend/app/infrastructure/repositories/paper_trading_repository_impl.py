from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.paper_trading import PaperTrade, Portfolio
from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.domain.services.trading_math import compute_pnl
from app.infrastructure.database.models.portfolio_model import PortfolioModel
from app.infrastructure.database.models.trade_model import TradeModel


def _portfolio_to_entity(model: PortfolioModel) -> Portfolio:
    return Portfolio(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        base_currency=model.base_currency,
        initial_balance=model.initial_balance,
        current_balance=model.current_balance,
        leverage=model.leverage,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _trade_to_entity(model: TradeModel) -> PaperTrade:
    return PaperTrade(
        id=model.id,
        portfolio_id=model.portfolio_id,
        signal_id=model.signal_id,
        symbol=model.symbol,
        side=model.side,
        entry_price=model.entry_price,
        exit_price=model.exit_price,
        quantity=model.quantity,
        stop_loss=model.stop_loss,
        take_profit=model.take_profit,
        trailing_stop_distance=model.trailing_stop_distance,
        margin_used=model.margin_used,
        realized_pnl=model.realized_pnl,
        status=model.status,
        pnl=model.pnl,
        opened_at=model.opened_at,
        closed_at=model.closed_at,
    )


class SqlAlchemyPaperTradingRepository(PaperTradingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_portfolio(self, portfolio: Portfolio) -> Portfolio:
        model = PortfolioModel(
            id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            base_currency=portfolio.base_currency,
            initial_balance=portfolio.initial_balance,
            current_balance=portfolio.current_balance,
            leverage=portfolio.leverage,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _portfolio_to_entity(model)

    async def list_portfolios(self, user_id: UUID) -> list[Portfolio]:
        result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.user_id == user_id)
        )
        return [_portfolio_to_entity(model) for model in result.scalars().all()]

    async def get_portfolio(self, portfolio_id: UUID, user_id: UUID) -> Portfolio | None:
        result = await self.session.execute(
            select(PortfolioModel).where(
                PortfolioModel.id == portfolio_id, PortfolioModel.user_id == user_id
            )
        )
        model = result.scalar_one_or_none()
        return _portfolio_to_entity(model) if model else None

    async def open_trade(self, trade: PaperTrade) -> PaperTrade:
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
            trailing_stop_distance=trade.trailing_stop_distance,
            margin_used=trade.margin_used,
            realized_pnl=trade.realized_pnl,
            status=trade.status,
            is_paper=True,
            pnl=trade.pnl,
            closed_at=trade.closed_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _trade_to_entity(model)

    async def get_trade(self, trade_id: UUID) -> PaperTrade | None:
        result = await self.session.execute(select(TradeModel).where(TradeModel.id == trade_id))
        model = result.scalar_one_or_none()
        return _trade_to_entity(model) if model else None

    async def list_trades(self, portfolio_id: UUID, status: str | None) -> list[PaperTrade]:
        query = select(TradeModel).where(TradeModel.portfolio_id == portfolio_id)
        if status is not None:
            query = query.where(TradeModel.status == status)
        query = query.order_by(TradeModel.opened_at.desc())
        result = await self.session.execute(query)
        return [_trade_to_entity(model) for model in result.scalars().all()]

    async def get_open_trades_for_symbol(self, symbol: str) -> list[PaperTrade]:
        result = await self.session.execute(
            select(TradeModel).where(
                TradeModel.symbol == symbol,
                TradeModel.status == "open",
                TradeModel.portfolio_id.isnot(None),
            )
        )
        return [_trade_to_entity(model) for model in result.scalars().all()]

    async def _apply_portfolio_pnl(self, portfolio_id: UUID, pnl: float) -> None:
        portfolio_result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        )
        portfolio_model = portfolio_result.scalar_one_or_none()
        if portfolio_model is not None:
            portfolio_model.current_balance += pnl

    async def close_trade(
        self, trade_id: UUID, exit_price: float, closed_at: datetime
    ) -> PaperTrade | None:
        result = await self.session.execute(select(TradeModel).where(TradeModel.id == trade_id))
        model = result.scalar_one_or_none()
        if model is None or model.status != "open":
            return None

        final_chunk_pnl = compute_pnl(
            model.symbol, model.side, model.entry_price, exit_price, model.quantity
        )
        total_pnl = model.realized_pnl + final_chunk_pnl

        model.exit_price = exit_price
        model.pnl = total_pnl
        model.status = "closed"
        model.closed_at = closed_at

        if model.portfolio_id is not None:
            await self._apply_portfolio_pnl(model.portfolio_id, final_chunk_pnl)

        await self.session.commit()
        await self.session.refresh(model)
        return _trade_to_entity(model)

    async def partial_close_trade(
        self, trade_id: UUID, close_quantity: float, exit_price: float, closed_at: datetime
    ) -> PaperTrade | None:
        result = await self.session.execute(select(TradeModel).where(TradeModel.id == trade_id))
        model = result.scalar_one_or_none()
        if model is None or model.status != "open":
            return None
        if close_quantity <= 0 or close_quantity >= model.quantity:
            return None

        chunk_pnl = compute_pnl(
            model.symbol, model.side, model.entry_price, exit_price, close_quantity
        )
        remaining_quantity = model.quantity - close_quantity

        model.realized_pnl += chunk_pnl
        if model.margin_used is not None:
            model.margin_used = model.margin_used * (remaining_quantity / model.quantity)
        model.quantity = remaining_quantity

        if model.portfolio_id is not None:
            await self._apply_portfolio_pnl(model.portfolio_id, chunk_pnl)

        await self.session.commit()
        await self.session.refresh(model)
        return _trade_to_entity(model)

    async def evaluate_and_close_if_triggered(
        self, trade: PaperTrade, current_price: float
    ) -> PaperTrade | None:
        triggered_price = None
        if trade.side == "long":
            if trade.stop_loss is not None and current_price <= trade.stop_loss:
                triggered_price = trade.stop_loss
            elif trade.take_profit is not None and current_price >= trade.take_profit:
                triggered_price = trade.take_profit
        else:
            if trade.stop_loss is not None and current_price >= trade.stop_loss:
                triggered_price = trade.stop_loss
            elif trade.take_profit is not None and current_price <= trade.take_profit:
                triggered_price = trade.take_profit

        if triggered_price is None:
            return None

        return await self.close_trade(trade.id, triggered_price, datetime.now(UTC))

    async def apply_trailing_stop(self, trade: PaperTrade, current_price: float) -> None:
        if trade.trailing_stop_distance is None or trade.trailing_stop_distance <= 0:
            return

        result = await self.session.execute(select(TradeModel).where(TradeModel.id == trade.id))
        model = result.scalar_one_or_none()
        if model is None or model.status != "open":
            return

        if model.side == "long":
            candidate = current_price - model.trailing_stop_distance
            if model.stop_loss is None or candidate > model.stop_loss:
                model.stop_loss = candidate
                await self.session.commit()
        else:
            candidate = current_price + model.trailing_stop_distance
            if model.stop_loss is None or candidate < model.stop_loss:
                model.stop_loss = candidate
                await self.session.commit()

    async def get_open_margin_used(self, portfolio_id: UUID) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(TradeModel.margin_used), 0.0)).where(
                TradeModel.portfolio_id == portfolio_id, TradeModel.status == "open"
            )
        )
        return float(result.scalar_one())

    async def get_open_trade_count(self, portfolio_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(TradeModel.id)).where(
                TradeModel.portfolio_id == portfolio_id, TradeModel.status == "open"
            )
        )
        return int(result.scalar_one())

    async def get_daily_pnl_pct(self, portfolio_id: UUID) -> float:
        portfolio_result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        )
        portfolio_model = portfolio_result.scalar_one_or_none()
        if portfolio_model is None or portfolio_model.initial_balance == 0:
            return 0.0

        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.coalesce(func.sum(TradeModel.pnl), 0.0)).where(
                TradeModel.portfolio_id == portfolio_id,
                TradeModel.status == "closed",
                TradeModel.closed_at >= today_start,
            )
        )
        daily_pnl = float(result.scalar_one())
        return (daily_pnl / portfolio_model.initial_balance) * 100

    async def get_account_open_trade_count(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(TradeModel.id))
            .join(PortfolioModel, TradeModel.portfolio_id == PortfolioModel.id)
            .where(PortfolioModel.user_id == user_id, TradeModel.status == "open")
        )
        return int(result.scalar_one())

    async def get_account_daily_pnl_pct(self, user_id: UUID) -> float:
        portfolios_result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.user_id == user_id)
        )
        portfolios = portfolios_result.scalars().all()
        total_initial_balance = sum(model.initial_balance for model in portfolios)
        if total_initial_balance == 0:
            return 0.0

        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.coalesce(func.sum(TradeModel.pnl), 0.0))
            .join(PortfolioModel, TradeModel.portfolio_id == PortfolioModel.id)
            .where(
                PortfolioModel.user_id == user_id,
                TradeModel.status == "closed",
                TradeModel.closed_at >= today_start,
            )
        )
        daily_pnl = float(result.scalar_one())
        return (daily_pnl / total_initial_balance) * 100
