from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Float, Text, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class HistoricalWaste(Base):
    __tablename__ = "historical_waste"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("waste_sources.id", ondelete="SET NULL"), nullable=True)
    measurement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(30), default="1_DAY", nullable=False)
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="tonnes", nullable=False)
    waste_category: Mapped[str] = mapped_column(String(50), default="MIXED", nullable=False)
    measurement_method: Mapped[str] = mapped_column(String(50), default="WEIGHBRIDGE", nullable=False)
    data_source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)
    quality_status: Mapped[str] = mapped_column(String(30), default="MEASURED", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_hist_waste_hab_date_src", "habitation_id", "measurement_date", "source_id"),
        CheckConstraint("quantity >= 0", name="chk_quantity_positive"),
    )
