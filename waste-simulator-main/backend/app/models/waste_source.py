from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class WasteSource(Base):
    __tablename__ = "waste_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    units_count: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    rate_per_unit_kg_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    daily_waste_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    organic_pct: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    recyclable_pct: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
