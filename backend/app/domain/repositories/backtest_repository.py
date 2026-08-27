from abc import ABC, abstractmethod

from app.domain.entities.backtest import Metric, Signal, Strategy, Trade


class BacktestRepository(ABC):
    @abstractmethod
    async def get_or_create_strategy(self, name: str, description: str | None, parameters: dict) -> Strategy:
        raise NotImplementedError

    @abstractmethod
    async def save_signal(self, signal: Signal) -> Signal:
        raise NotImplementedError

    @abstractmethod
    async def save_trade(self, trade: Trade) -> Trade:
        raise NotImplementedError

    @abstractmethod
    async def save_metrics(self, metrics: list[Metric]) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list_signals(self, symbol: str | None, limit: int) -> list[Signal]:
        raise NotImplementedError

    @abstractmethod
    async def list_strategies(self) -> list[Strategy]:
        raise NotImplementedError