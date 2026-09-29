from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    strategy_type: Mapped[str] = mapped_column(String(60), nullable=False)
    collection_efficiency_pct: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    segregation_efficiency_pct: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    diversion_percent: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    treatment_capacity_kg: Mapped[float] = mapped_column(Float, default=5000.0, nullable=False)
    estimated_cost_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    environmental_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(60), nullable=False)
    overrides: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
