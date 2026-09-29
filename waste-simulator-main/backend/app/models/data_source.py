from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, default=2024, nullable=False)
    reference_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    document_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_quality: Mapped[str] = mapped_column(String(40), default="OFFICIAL", nullable=False)
    verification_status: Mapped[str] = mapped_column(String(40), default="VERIFIED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
