"""Disaster & Environmental Emergency Models for SWMS."""
from datetime import datetime, date, timezone
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DisasterEvent(Base):
    __tablename__ = "disaster_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    habitation_id: Mapped[int] = mapped_column(Integer, nullable=True)
    disaster_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Flood, Cyclone, Landslide, Drought, Earthquake, Tsunami, Extreme Heat, Wildfire, Other
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=7)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH")  # LOW, MEDIUM, HIGH, EXTREME
    warning_level: Mapped[str] = mapped_column(String(20), default="ORANGE")  # GREEN, YELLOW, ORANGE, RED
    affected_area_sqkm: Mapped[float] = mapped_column(Float, default=15.0)
    affected_population: Mapped[float] = mapped_column(Float, default=5000.0)
    displaced_population: Mapped[float] = mapped_column(Float, default=2000.0)
    temporary_population: Mapped[float] = mapped_column(Float, default=1000.0)
    phase: Mapped[str] = mapped_column(String(50), default="DURING")  # BEFORE, DURING, IMMEDIATE_RESPONSE, RECOVERY, POST_NORMALIZATION
    status: Mapped[str] = mapped_column(String(50), default="PLANNED_DISASTER")  # PLANNED_DISASTER, ACTIVE_DISASTER, HISTORICAL_DISASTER
    source: Mapped[str] = mapped_column(String(100), default="District Disaster Management Authority (DDMA)")
    data_quality: Mapped[str] = mapped_column(String(20), default="SCENARIO")
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), default="System Planner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    impacts = relationship("DisasterImpact", back_populates="event", cascade="all, delete-orphan")
    daily_analyses = relationship("DisasterDailyAnalysis", back_populates="event", cascade="all, delete-orphan")

class DisasterImpact(Base):
    __tablename__ = "disaster_impacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_event_id: Mapped[int] = mapped_column(Integer, ForeignKey("disaster_events.id"), nullable=False, index=True)
    infrastructure_damage_factor: Mapped[float] = mapped_column(Float, default=0.20)  # 20% infrastructure damaged
    road_access_factor: Mapped[float] = mapped_column(Float, default=0.50)  # 50% roads accessible
    collection_access_factor: Mapped[float] = mapped_column(Float, default=0.60)
    vehicle_availability_factor: Mapped[float] = mapped_column(Float, default=0.70)
    collection_efficiency_factor: Mapped[float] = mapped_column(Float, default=0.60)  # 60% collection efficiency
    waste_generation_factor: Mapped[float] = mapped_column(Float, default=1.25)  # 25% surge in domestic/emergency waste
    treatment_capacity_factor: Mapped[float] = mapped_column(Float, default=0.80)  # 80% treatment capacity available
    disposal_capacity_factor: Mapped[float] = mapped_column(Float, default=0.75)
    additional_waste_pct: Mapped[float] = mapped_column(Float, default=25.0)  # 25% surge
    debris_factor: Mapped[float] = mapped_column(Float, default=2.5)  # Tonnes of debris/silt per day
    emergency_waste_factor: Mapped[float] = mapped_column(Float, default=1.5)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    event = relationship("DisasterEvent", back_populates="impacts")

class EmergencyShelter(Base):
    __tablename__ = "emergency_shelters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    shelter_code: Mapped[str] = mapped_column(String(50), nullable=True)
    capacity_persons: Mapped[int] = mapped_column(Integer, default=500)
    current_population: Mapped[int] = mapped_column(Integer, default=350)
    waste_per_person_kg_day: Mapped[float] = mapped_column(Float, default=0.50)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, STANDBY, CLOSED
    source: Mapped[str] = mapped_column(String(100), default="Taluk Relief Officer")
    notes: Mapped[str] = mapped_column(String(300), nullable=True)

class DisasterDailyAnalysis(Base):
    __tablename__ = "disaster_daily_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_event_id: Mapped[int] = mapped_column(Integer, ForeignKey("disaster_events.id"), nullable=False, index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    normal_waste_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    temporary_pop_waste_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    disaster_additional_waste_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    debris_cleanup_waste_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    total_generated_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    effective_collection_cap_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    collected_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    uncollected_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    cumulative_accumulated_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    effective_treatment_cap_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    treated_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    treatment_gap_tonnes: Mapped[float] = mapped_column(Float, default=0.0)
    effective_vehicles_required: Mapped[int] = mapped_column(Integer, default=0)
    vehicle_deficit: Mapped[int] = mapped_column(Integer, default=0)

    event = relationship("DisasterEvent", back_populates="daily_analyses")

class DisasterScenario(Base):
    __tablename__ = "disaster_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    disaster_type: Mapped[str] = mapped_column(String(50), default="Flood")
    severity: Mapped[str] = mapped_column(String(20), default="HIGH")
    duration_days: Mapped[int] = mapped_column(Integer, default=7)
    affected_population: Mapped[float] = mapped_column(Float, default=5000.0)
    displaced_population: Mapped[float] = mapped_column(Float, default=2000.0)
    shelter_population: Mapped[float] = mapped_column(Float, default=1500.0)
    road_access_pct: Mapped[float] = mapped_column(Float, default=50.0)
    collection_efficiency_pct: Mapped[float] = mapped_column(Float, default=60.0)
    treatment_capacity_pct: Mapped[float] = mapped_column(Float, default=80.0)
    additional_waste_pct: Mapped[float] = mapped_column(Float, default=25.0)
    debris_tonnes_day: Mapped[float] = mapped_column(Float, default=2.5)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DisasterFacilityImpact(Base):
    __tablename__ = "disaster_facility_impacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_event_id: Mapped[int] = mapped_column(Integer, ForeignKey("disaster_events.id"), nullable=False, index=True)
    facility_id: Mapped[int] = mapped_column(Integer, ForeignKey("facilities.id"), nullable=False)
    operational_status_override: Mapped[str] = mapped_column(String(50), default="PARTIAL_DISRUPTION")
    effective_capacity_kg_day: Mapped[float] = mapped_column(Float, default=0.0)
    damage_assessment: Mapped[str] = mapped_column(String(300), nullable=True)
