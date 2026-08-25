from datetime import datetime

from pydantic import BaseModel


class CandleResponse(BaseModel):
    symbol: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    timestamp: datetime


class InstrumentResponse(BaseModel):
    symbol: str


class MarketStatusResponse(BaseModel):
    instruments: list[str]
    active_sessions: list[str]


class BackfillRequest(BaseModel):
    symbol: str
    interval: str = "1min"
    output_size: int = 100


class BackfillResponse(BaseModel):
    symbol: str
    interval: str
    stored: int
