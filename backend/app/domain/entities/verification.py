from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class VerificationCode:
    id: UUID
    user_id: UUID
    purpose: str
    code_hash: str
    expires_at: datetime
    consumed_at: datetime | None
    created_at: datetime
