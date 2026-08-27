from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
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

    async def _close(
        self, trade_id: UUID, exit_price: float, closed_at: datetime
    ) -> PaperTrade | None:
        result = await self.session.execute(select(TradeModel).where(TradeModel.id == trade_id))
        model = result.scalar_one_or_none()
        if model is None or model.status != "open":
            return None

        pnl = compute_pnl(model.symbol, model.side, model.entry_price, exit_price, model.quantity)
        model.exit_price = exit_price
        model.pnl = pnl
        model.status = "closed"
        model.closed_at = closed_at

        if model.portfolio_id is not None:
            portfolio_result = await self.session.execute(
                select(PortfolioModel).where(PortfolioModel.id == model.portfolio_id)
            )
            portfolio_model = portfolio_result.scalar_one_or_none()
            if portfolio_model is not None:
                portfolio_model.current_balance += pnl

        await self.session.commit()
        await self.session.refresh(model)
        return _trade_to_entity(model)

    async def close_trade(
        self, trade_id: UUID, exit_price: float, closed_at: datetime
    ) -> PaperTrade | None:
        return await self._close(trade_id, exit_price, closed_at)

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

        return await self._close(trade.id, triggered_price, datetime.now(UTC))
