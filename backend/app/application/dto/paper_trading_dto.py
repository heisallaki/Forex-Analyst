from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreatePortfolioRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    initial_balance: float = Field(default=10000.0, gt=0)
    base_currency: str = "USD"


class PortfolioResponse(BaseModel):
    id: str
    name: str
    base_currency: str
    initial_balance: float
    current_balance: float
    created_at: datetime


class OpenTradeRequest(BaseModel):
    portfolio_id: str
    symbol: str
    side: Literal["long", "short"]
    quantity: float | None = Field(default=None, gt=0)
    risk_amount: float | None = Field(default=None, gt=0)
    stop_loss: float | None = None
    take_profit: float | None = None
    signal_id: str | None = None


class TradeResponse(BaseModel):
    id: str
    portfolio_id: str
    signal_id: str | None
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


class CloseTradeRequest(BaseModel):
    exit_price: float | None = None


class PortfolioPerformanceResponse(BaseModel):
    current_balance: float
    initial_balance: float
    return_pct: float
    total_trades: int
    open_trades: int
    win_rate: float | None
    profit_factor: float | None
    gross_profit: float
    gross_loss: float
    total_pnl: float
