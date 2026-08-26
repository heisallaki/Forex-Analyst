from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AIPrediction:
    id: UUID
    model_name: str
    symbol: str
    prediction_type: str
    output: dict
    created_at: datetime | None
