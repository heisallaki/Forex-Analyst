from typing import Literal

from pydantic import BaseModel, Field


class SubmitOrderRequest(BaseModel):
    symbol: str
    side: Literal["long", "short"]
    quantity: float = Field(gt=0)
    stop_loss: float | None = None
    take_profit: float | None = None
    confirmation_phrase: str


class ExecutionResultResponse(BaseModel):
    status: Literal["rejected", "accepted"]
    reason: str
    broker_order_id: str | None


class ExecutionStatusResponse(BaseModel):
    execution_enabled: bool
    max_position_size: float
    max_open_positions: int
    max_daily_loss_pct: float
    broker_configured: bool
