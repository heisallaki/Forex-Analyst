from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.paper_trading import PaperTrade, Portfolio


class PaperTradingRepository(ABC):
    @abstractmethod
    async def create_portfolio(self, portfolio: Portfolio) -> Portfolio:
        raise NotImplementedError

    @abstractmethod
    async def list_portfolios(self, user_id: UUID) -> list[Portfolio]:
        raise NotImplementedError

    @abstractmethod
    async def get_portfolio(self, portfolio_id: UUID, user_id: UUID) -> Portfolio | None:
        raise NotImplementedError

    @abstractmethod
    async def open_trade(self, trade: PaperTrade) -> PaperTrade:
        raise NotImplementedError

    @abstractmethod
    async def get_trade(self, trade_id: UUID) -> PaperTrade | None:
        raise NotImplementedError

    @abstractmethod
    async def list_trades(self, portfolio_id: UUID, status: str | None) -> list[PaperTrade]:
        raise NotImplementedError

    @abstractmethod
    async def get_open_trades_for_symbol(self, symbol: str) -> list[PaperTrade]:
        raise NotImplementedError

    @abstractmethod
    async def close_trade(
        self, trade_id: UUID, exit_price: float, closed_at: datetime
    ) -> PaperTrade | None:
        raise NotImplementedError

    @abstractmethod
    async def evaluate_and_close_if_triggered(
        self, trade: PaperTrade, current_price: float
    ) -> PaperTrade | None:
        raise NotImplementedError
