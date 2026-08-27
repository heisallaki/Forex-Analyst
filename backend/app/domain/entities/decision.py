from dataclasses import dataclass
from datetime import datetime


@dataclass
class Recommendation:
    symbol: str
    interval: str
    generated_at: datetime
    action: str
    trend: str
    confidence: float
    risk_level: str
    expected_reward_atr: float
    expected_risk_atr: float
    reward_risk_ratio: float | None
    market_regime: str
    supporting_indicators: list[str]
    reasoning: str
    alternative_scenarios: list[str]
    invalidation_conditions: list[str]
