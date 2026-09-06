from datetime import datetime

from pydantic import BaseModel, Field


class SystemSettingsResponse(BaseModel):
    min_confidence_threshold: float
    min_reward_risk_ratio: float
    updated_at: datetime
    updated_by: str | None


class UpdateSystemSettingsRequest(BaseModel):
    min_confidence_threshold: float = Field(gt=0, lt=1)
    min_reward_risk_ratio: float = Field(gt=0)
