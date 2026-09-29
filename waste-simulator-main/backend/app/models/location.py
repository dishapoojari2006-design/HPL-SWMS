from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location_type: Mapped[str] = mapped_column(String(60), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    state: Mapped[str] = mapped_column(String(100), default="Karnataka", nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    taluk: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    municipality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    panchayat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ward: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    village: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    area: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    area_unit: Mapped[str] = mapped_column(String(30), default="sq_km", nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geometry: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    terrain: Mapped[str] = mapped_column(String(60), default="Plain", nullable=False)
    classification: Mapped[str] = mapped_column(String(60), default="SEMI_URBAN", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String(120), default="OFFICIAL_RECORD", nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, default=2024, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
