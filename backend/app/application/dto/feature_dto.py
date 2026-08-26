from datetime import datetime

from pydantic import BaseModel


class FeatureRow(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    sma_20: float | None
    ema_20: float | None
    vwap: float | None
    atr_14: float | None
    rsi_14: float | None
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None
    adx_14: float | None
    plus_di_14: float | None
    minus_di_14: float | None
    bollinger_upper: float | None
    bollinger_middle: float | None
    bollinger_lower: float | None
    swing_high: bool
    swing_low: bool
    market_structure: str
    liquidity_sweep: str | None
    order_block: str | None
    fair_value_gap: str | None
    volatility: float | None
    trend_strength: float | None
    momentum: float | None
    active_sessions: list[str]
