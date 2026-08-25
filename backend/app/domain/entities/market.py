from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    symbol: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    timestamp: datetime


@dataclass
class Tick:
    symbol: str
    price: float
    timestamp: datetime
