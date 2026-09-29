from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DemographyParameter(Base):
    __tablename__ = "demography_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    total_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    male_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    female_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    other_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    population_growth_rate: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    number_of_households: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_household_size: Mapped[float] = mapped_column(Float, default=4.5, nullable=False)
    population_density: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    floating_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    seasonal_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tourist_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    migrant_population: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pop_reference_year: Mapped[int] = mapped_column(Integer, default=2024, nullable=False)
    census_source: Mapped[str] = mapped_column(String(120), default="Census 2011 / Survey Projection", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class InfrastructureParameter(Base):
    __tablename__ = "infrastructure_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    collection_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    waste_bins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    community_bins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vehicle_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    vehicle_capacity_kg: Mapped[float] = mapped_column(Float, default=2000.0, nullable=False)
    trips_per_vehicle: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    collection_frequency_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    collection_coverage_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    treatment_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    composting_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recycling_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    mrf_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wte_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    landfill_capacity_kg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    workers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    working_hours_day: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class IndustrialParameter(Base):
    __tablename__ = "industrial_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    number_of_industries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    industrial_waste_kg_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    industrial_growth_rate: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    commercial_waste_kg_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    market_waste_kg_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    construction_waste_kg_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    commercial_establishments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hazardous_category: Mapped[str] = mapped_column(String(50), default="NONE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class WasteComposition(Base):
    __tablename__ = "waste_compositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habitation_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    organic_percent: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    food_percent: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    paper_percent: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    plastic_percent: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    glass_percent: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    metal_percent: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    textile_percent: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    ewaste_percent: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    other_percent: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
