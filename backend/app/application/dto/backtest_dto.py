from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ConditionSchema(BaseModel):
    field: str
    operator: Literal["lt", "lte", "gt", "gte", "eq", "neq"]
    value: float | str | None = None
    compare_field: str | None = None

    @model_validator(mode="after")
    def validate_value_or_compare_field(self):
        if self.value is None and self.compare_field is None:
            raise ValueError("Either value or compare_field must be provided")
        if self.value is not None and self.compare_field is not None:
            raise ValueError("Provide only one of value or compare_field, not both")
        return self


class RuleGroupSchema(BaseModel):
    match: Literal["all", "any"] = "all"
    conditions: list[ConditionSchema] = Field(default_factory=list)


class BacktestRunRequest(BaseModel):
    symbol: str
    intervals: list[str] = Field(default_factory=lambda: ["1min"])
    limit: int = Field(default=500, ge=50, le=5000)
    strategy_name: str
    strategy_description: str | None = None
    entry_long_rules: RuleGroupSchema | None = None
    entry_short_rules: RuleGroupSchema | None = None
    initial_balance: float = 10000.0
    risk_per_trade_pct: float = Field(default=1.0, gt=0, le=100)
    spread_pips: float = Field(default=1.0, ge=0)
    slippage_pips: float = Field(default=0.5, ge=0)
    commission_per_trade: float = Field(default=0.0, ge=0)
    stop_loss_atr_multiple: float = Field(default=1.5, gt=0)
    take_profit_atr_multiple: float = Field(default=3.0, gt=0)
    max_holding_bars: int = Field(default=200, gt=0)

    @model_validator(mode="after")
    def validate_entry_rules(self):
        has_long = self.entry_long_rules is not None and len(self.entry_long_rules.conditions) > 0
        has_short = self.entry_short_rules is not None and len(self.entry_short_rules.conditions) > 0
        if not has_long and not has_short:
            raise ValueError("At least one of entry_long_rules or entry_short_rules must have conditions")
        return self


class TradeResultSchema(BaseModel):
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    r_multiple: float | None
    opened_at: datetime
    closed_at: datetime
    exit_reason: str


class BacktestStatisticsSchema(BaseModel):
    total_trades: int
    win_rate: float | None
    profit_factor: float | None
    gross_profit: float
    gross_loss: float
    average_r_multiple: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown_pct: float
    final_equity: float
    monthly_performance: dict[str, float]


class BacktestIntervalResult(BaseModel):
    interval: str
    trades: list[TradeResultSchema]
    statistics: BacktestStatisticsSchema


class BacktestRunResponse(BaseModel):
    strategy_id: str
    strategy_name: str
    symbol: str
    results: list[BacktestIntervalResult]


class SignalListItem(BaseModel):
    id: str
    strategy_id: str | None
    symbol: str
    direction: str
    confidence: float
    reasoning: dict
    created_at: datetime
    hidden_at: datetime | None
    is_owner: bool


class SignalBulkActionRequest(BaseModel):
    signal_ids: list[str]


class SignalBulkActionResponse(BaseModel):
    succeeded: list[str]
    skipped: list[str]


class StrategyListItem(BaseModel):
    id: str
    name: str
    description: str | None
    is_active: bool