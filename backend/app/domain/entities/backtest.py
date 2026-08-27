from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Strategy:
    id: UUID
    name: str
    description: str | None
    parameters: dict
    is_active: bool


@dataclass
class Signal:
    id: UUID
    strategy_id: UUID | None
    symbol: str
    direction: str
    confidence: float
    reasoning: dict
    created_at: datetime


@dataclass
class Trade:
    id: UUID
    signal_id: UUID | None
    symbol: str
    side: str
    entry_price: float
    exit_price: float | None
    quantity: float
    status: str
    is_paper: bool
    pnl: float | None
    opened_at: datetime
    closed_at: datetime | None
    portfolio_id: UUID | None = None
    stop_loss: float | None = None
    take_profit: float | None = None


@dataclass
class Metric:
    id: UUID
    name: str
    value: float
    tags: dict
    recorded_at: datetime
