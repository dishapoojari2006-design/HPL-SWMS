"""Pydantic Schemas for Disaster & Emergency Waste Management."""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

DisasterType = Literal[
    "Flood",
    "Flash Flood",
    "Urban Flood",
    "Coastal Flood",
    "Cyclone",
    "Severe Storm",
    "Heavy Rainfall",
    "Landslide",
    "Drought",
    "Earthquake",
    "Tsunami",
    "Extreme Heat",
    "Wildfire",
    "Other"
]

DisasterSeverity = Literal["LOW", "MEDIUM", "HIGH", "EXTREME"]
DisasterPhase = Literal["BEFORE", "DURING", "IMMEDIATE_RESPONSE", "RECOVERY", "POST_NORMALIZATION"]
DisasterStatus = Literal["PLANNED_DISASTER", "ACTIVE_DISASTER", "HISTORICAL_DISASTER"]

class DisasterEventCreate(BaseModel):
    location_id: int
    habitation_id: Optional[int] = None
    disaster_type: DisasterType = "Flood"
    name: str = Field(min_length=2, max_length=150)
    start_date: date
    end_date: Optional[date] = None
    duration_days: int = Field(default=7, ge=1, le=90)
    severity: DisasterSeverity = "HIGH"
    warning_level: str = "ORANGE"
    affected_area_sqkm: float = Field(default=15.0, ge=0.0)
    affected_population: float = Field(default=5000.0, ge=0.0)
    displaced_population: float = Field(default=2000.0, ge=0.0)
    temporary_population: float = Field(default=1000.0, ge=0.0)
    phase: DisasterPhase = "DURING"
    status: DisasterStatus = "PLANNED_DISASTER"
    source: str = "District Disaster Management Authority (DDMA)"
    data_quality: str = "SCENARIO"
    notes: Optional[str] = None

class DisasterImpactIn(BaseModel):
    infrastructure_damage_factor: float = Field(default=0.20, ge=0.0, le=1.0)
    road_access_factor: float = Field(default=0.50, ge=0.0, le=1.0)
    collection_access_factor: float = Field(default=0.60, ge=0.0, le=1.0)
    vehicle_availability_factor: float = Field(default=0.70, ge=0.0, le=1.0)
    collection_efficiency_factor: float = Field(default=0.60, ge=0.0, le=1.0)
    waste_generation_factor: float = Field(default=1.25, ge=0.5, le=5.0)
    treatment_capacity_factor: float = Field(default=0.80, ge=0.0, le=1.0)
    disposal_capacity_factor: float = Field(default=0.75, ge=0.0, le=1.0)
    additional_waste_pct: float = Field(default=25.0, ge=0.0, le=500.0)
    debris_factor: float = Field(default=2.5, ge=0.0)
    emergency_waste_factor: float = Field(default=1.5, ge=0.0)
    notes: Optional[str] = None

class DisasterImpactOut(DisasterImpactIn):
    id: int
    disaster_event_id: int
    model_config = ConfigDict(from_attributes=True)

class DisasterEventOut(DisasterEventCreate):
    id: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    impacts: List[DisasterImpactOut] = []
    model_config = ConfigDict(from_attributes=True)

class EmergencyShelterCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=150)
    shelter_code: Optional[str] = None
    capacity_persons: int = Field(default=500, ge=1)
    current_population: int = Field(default=350, ge=0)
    waste_per_person_kg_day: float = Field(default=0.50, ge=0.05, le=5.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "ACTIVE"
    source: str = "Taluk Relief Officer"
    notes: Optional[str] = None

class EmergencyShelterOut(EmergencyShelterCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DisasterScenarioCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=150)
    disaster_type: str = "Flood"
    severity: DisasterSeverity = "HIGH"
    duration_days: int = Field(default=7, ge=1, le=90)
    affected_population: float = Field(default=5000.0, ge=0.0)
    displaced_population: float = Field(default=2000.0, ge=0.0)
    shelter_population: float = Field(default=1500.0, ge=0.0)
    road_access_pct: float = Field(default=50.0, ge=0.0, le=100.0)
    collection_efficiency_pct: float = Field(default=60.0, ge=0.0, le=100.0)
    treatment_capacity_pct: float = Field(default=80.0, ge=0.0, le=100.0)
    additional_waste_pct: float = Field(default=25.0, ge=0.0, le=500.0)
    debris_tonnes_day: float = Field(default=2.5, ge=0.0)
    parameters: Optional[Dict[str, Any]] = None

class DisasterScenarioOut(DisasterScenarioCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DisasterAnalysisRequest(BaseModel):
    location_id: int
    disaster_type: str = "Flood"
    severity: DisasterSeverity = "HIGH"
    duration_days: int = Field(default=7, ge=1, le=60)
    affected_population: float = Field(default=5000.0, ge=0.0)
    displaced_population: float = Field(default=2000.0, ge=0.0)
    shelter_population: float = Field(default=1500.0, ge=0.0)
    road_access_pct: float = Field(default=50.0, ge=0.0, le=100.0)
    collection_efficiency_pct: float = Field(default=60.0, ge=0.0, le=100.0)
    treatment_capacity_pct: float = Field(default=80.0, ge=0.0, le=100.0)
    additional_waste_pct: float = Field(default=25.0, ge=0.0, le=500.0)
    debris_tonnes_day: float = Field(default=2.5, ge=0.0)

class DisasterWhatIfRequest(BaseModel):
    location_id: int
    baseline_scenario: DisasterAnalysisRequest
    modified_scenario: DisasterAnalysisRequest
