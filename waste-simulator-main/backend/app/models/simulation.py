from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    strategy_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    years: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    results: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
