from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import ConfigDict, BaseModel, Field

class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    location_type: str = Field(min_length=2, max_length=60)
    parent_id: Optional[int] = None
    country: str = "India"
    state: str = "Karnataka"
    district: Optional[str] = None
    taluk: Optional[str] = None
    municipality: Optional[str] = None
    panchayat: Optional[str] = None
    ward: Optional[str] = None
    village: Optional[str] = None
    area: Optional[float] = Field(None, ge=0)
    area_unit: str = "sq_km"
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    geometry: Optional[Dict[str, Any]] = None
    terrain: str = "Plain"
    classification: str = "SEMI_URBAN"
    description: Optional[str] = None
    data_source: str = "OFFICIAL_RECORD"
    source_year: int = Field(2024, ge=1900, le=2100)
    details: Dict[str, Any] = Field(default_factory=dict)

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    location_type: Optional[str] = None
    parent_id: Optional[int] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    municipality: Optional[str] = None
    panchayat: Optional[str] = None
    ward: Optional[str] = None
    village: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None
    terrain: Optional[str] = None
    classification: Optional[str] = None
    description: Optional[str] = None
    data_source: Optional[str] = None
    source_year: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

class LocationOut(BaseModel):
    id: int
    name: str
    location_type: str
    parent_id: Optional[int] = None
    country: str
    state: str
    district: Optional[str] = None
    taluk: Optional[str] = None
    municipality: Optional[str] = None
    panchayat: Optional[str] = None
    ward: Optional[str] = None
    village: Optional[str] = None
    area: Optional[float] = None
    area_unit: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None
    terrain: str
    classification: str
    description: Optional[str] = None
    data_source: str
    source_year: int
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HabitationCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=255)
    habitation_code: Optional[str] = None
    population: float = Field(0.0, ge=0)
    households: float = Field(0.0, ge=0)
    area_sq_km: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    terrain: str = "Plain"
    road_accessibility: str = "Good"
    data_quality: str = "SURVEYED"
    verification_status: str = "VERIFIED"

class HabitationUpdate(BaseModel):
    name: Optional[str] = None
    habitation_code: Optional[str] = None
    population: Optional[float] = None
    households: Optional[float] = None
    area_sq_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    terrain: Optional[str] = None
    road_accessibility: Optional[str] = None
    data_quality: Optional[str] = None
    verification_status: Optional[str] = None

class HabitationOut(BaseModel):
    id: int
    location_id: int
    name: str
    habitation_code: Optional[str] = None
    population: float
    households: float
    area_sq_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    terrain: str
    road_accessibility: str
    data_quality: str
    verification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
