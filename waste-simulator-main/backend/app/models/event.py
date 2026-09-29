from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    expected_attendance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    additional_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    waste_increase_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
