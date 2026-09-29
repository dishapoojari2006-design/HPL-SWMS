from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, BaseModel, Field, field_validator

class DemographyIn(BaseModel):
    habitation_id: int
    total_population: float = Field(..., ge=0)
    male_population: float = Field(0.0, ge=0)
    female_population: float = Field(0.0, ge=0)
    other_population: float = Field(0.0, ge=0)
    population_growth_rate: float = Field(2.0, ge=-10.0, le=25.0)
    number_of_households: float = Field(..., ge=0)
    average_household_size: float = Field(4.5, gt=0, le=50.0)
    population_density: float = Field(0.0, ge=0)
    floating_population: float = Field(0.0, ge=0)
    seasonal_population: float = Field(0.0, ge=0)
    tourist_population: float = Field(0.0, ge=0)
    migrant_population: float = Field(0.0, ge=0)
    pop_reference_year: int = Field(2024, ge=1900, le=2100)
    census_source: str = "Census 2011 / Survey Projection"

class DemographyOut(DemographyIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InfrastructureIn(BaseModel):
    habitation_id: int
    collection_points: int = Field(0, ge=0)
    waste_bins: int = Field(0, ge=0)
    community_bins: int = Field(0, ge=0)
    vehicle_count: int = Field(1, ge=0)
    vehicle_capacity_kg: float = Field(2000.0, gt=0)
    trips_per_vehicle: int = Field(1, ge=1, le=20)
    collection_frequency_days: int = Field(1, ge=1, le=30)
    collection_coverage_percent: float = Field(100.0, ge=0, le=100.0)
    treatment_capacity_kg: float = Field(0.0, ge=0)
    composting_capacity_kg: float = Field(0.0, ge=0)
    recycling_capacity_kg: float = Field(0.0, ge=0)
    mrf_capacity_kg: float = Field(0.0, ge=0)
    wte_capacity_kg: float = Field(0.0, ge=0)
    landfill_capacity_kg: float = Field(0.0, ge=0)
    workers_count: int = Field(0, ge=0)
    working_hours_day: float = Field(8.0, ge=1.0, le=24.0)

class InfrastructureOut(InfrastructureIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IndustrialIn(BaseModel):
    habitation_id: int
    number_of_industries: int = Field(0, ge=0)
    industrial_waste_kg_day: float = Field(0.0, ge=0)
    industrial_growth_rate: float = Field(2.0, ge=-20.0, le=50.0)
    commercial_waste_kg_day: float = Field(0.0, ge=0)
    market_waste_kg_day: float = Field(0.0, ge=0)
    construction_waste_kg_day: float = Field(0.0, ge=0)
    commercial_establishments: int = Field(0, ge=0)
    hazardous_category: str = "NONE"

class IndustrialOut(IndustrialIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CompositionIn(BaseModel):
    habitation_id: int
    organic_percent: float = Field(50.0, ge=0, le=100.0)
    food_percent: float = Field(15.0, ge=0, le=100.0)
    paper_percent: float = Field(10.0, ge=0, le=100.0)
    plastic_percent: float = Field(10.0, ge=0, le=100.0)
    glass_percent: float = Field(4.0, ge=0, le=100.0)
    metal_percent: float = Field(3.0, ge=0, le=100.0)
    textile_percent: float = Field(4.0, ge=0, le=100.0)
    ewaste_percent: float = Field(2.0, ge=0, le=100.0)
    other_percent: float = Field(2.0, ge=0, le=100.0)

    @field_validator("other_percent")
    @classmethod
    def validate_total_100(cls, v, info):
        values = info.data
        total = (
            values.get("organic_percent", 0) +
            values.get("food_percent", 0) +
            values.get("paper_percent", 0) +
            values.get("plastic_percent", 0) +
            values.get("glass_percent", 0) +
            values.get("metal_percent", 0) +
            values.get("textile_percent", 0) +
            values.get("ewaste_percent", 0) +
            v
        )
        if round(total, 2) != 100.0:
            raise ValueError(f"Waste composition percentages must sum to exactly 100% (currently sums to {round(total, 2)}%)")
        return v

class CompositionOut(CompositionIn):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
