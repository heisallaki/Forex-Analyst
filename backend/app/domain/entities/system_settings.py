from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SystemSettings:
    id: UUID
    min_confidence_threshold: float
    min_reward_risk_ratio: float
    updated_at: datetime
    updated_by: UUID | None
