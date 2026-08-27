from dataclasses import dataclass


@dataclass
class ExecutionOrderRequest:
    symbol: str
    side: str
    quantity: float
    stop_loss: float | None
    take_profit: float | None
    confirmation_phrase: str


@dataclass
class ExecutionResult:
    status: str
    reason: str
    broker_order_id: str | None
