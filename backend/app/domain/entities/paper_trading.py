from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Portfolio:
    id: UUID
    user_id: UUID
    name: str
    base_currency: str
    initial_balance: float
    current_balance: float
    created_at: datetime
    updated_at: datetime


@dataclass
class PaperTrade:
    id: UUID
    portfolio_id: UUID
    signal_id: UUID | None
    symbol: str
    side: str
    entry_price: float
    exit_price: float | None
    quantity: float
    stop_loss: float | None
    take_profit: float | None
    status: str
    pnl: float | None
    opened_at: datetime
    closed_at: datetime | None
