from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Habitation(Base):
    __tablename__ = "habitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    habitation_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    households: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    area_sq_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    terrain: Mapped[str] = mapped_column(String(60), default="Plain", nullable=False)
    road_accessibility: Mapped[str] = mapped_column(String(60), default="Good", nullable=False)
    data_quality: Mapped[str] = mapped_column(String(40), default="SURVEYED", nullable=False)
    verification_status: Mapped[str] = mapped_column(String(40), default="VERIFIED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
