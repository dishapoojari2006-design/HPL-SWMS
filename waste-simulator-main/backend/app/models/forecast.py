from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Float, Text, JSON, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    habitation_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    forecast_period: Mapped[str] = mapped_column(String(50), nullable=False)
    method_used: Mapped[str] = mapped_column(String(50), nullable=False)
    training_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    training_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    forecast_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="tonnes", nullable=False)
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mape: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_level: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)
    limitations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_forecast_loc_period", "location_id", "forecast_period"),
        CheckConstraint("forecast_value >= 0", name="chk_forecast_positive"),
    )
