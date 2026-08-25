import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class TickModel(Base):
    __tablename__ = "ticks"
    __table_args__ = (PrimaryKeyConstraint("id", "timestamp", name="ticks_pkey"),)

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
