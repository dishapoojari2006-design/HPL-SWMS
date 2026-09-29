from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import ConfigDict, BaseModel, Field

class WasteSourceCreate(BaseModel):
    habitation_id: int
    source_type: str = Field(..., description="HOUSEHOLD, INDUSTRY, HOSPITAL, CLINIC, SCHOOL, COLLEGE, HOSTEL, HOTEL, RESTAURANT, MARKET, SHOP, OFFICE, GOVERNMENT, RELIGIOUS, COMMUNITY, TOURISM, EVENT, CONSTRUCTION, FLOATING, OTHER")
    name: str = Field(min_length=2, max_length=255)
    units_count: float = Field(1.0, ge=0)
    rate_per_unit_kg_day: float = Field(0.0, ge=0)
    daily_waste_kg: float = Field(0.0, ge=0)
    organic_pct: float = Field(50.0, ge=0, le=100.0)
    recyclable_pct: float = Field(30.0, ge=0, le=100.0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    details: Dict[str, Any] = Field(default_factory=dict)

class WasteSourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    units_count: Optional[float] = None
    rate_per_unit_kg_day: Optional[float] = None
    daily_waste_kg: Optional[float] = None
    organic_pct: Optional[float] = None
    recyclable_pct: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class WasteSourceOut(WasteSourceCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FacilityCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=255)
    facility_type: str = Field(..., description="Composting, MRF, WTE, Landfill, Transfer Station")
    capacity_kg_day: float = Field(0.0, ge=0)
    current_utilization_kg_day: float = Field(0.0, ge=0)
    operating_status: str = "Operational"
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    capacity_kg_day: Optional[float] = None
    current_utilization_kg_day: Optional[float] = None
    operating_status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FacilityOut(FacilityCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventCreate(BaseModel):
    habitation_id: int
    name: str = Field(min_length=2, max_length=255)
    event_type: str = "Festival"
    expected_attendance: float = Field(0.0, ge=0)
    additional_population: float = Field(0.0, ge=0)
    duration_days: int = Field(1, ge=1, le=365)
    waste_increase_percent: float = Field(0.0, ge=0, le=500.0)
    details: Dict[str, Any] = Field(default_factory=dict)

class EventUpdate(BaseModel):
    name: Optional[str] = None
    event_type: Optional[str] = None
    expected_attendance: Optional[float] = None
    additional_population: Optional[float] = None
    duration_days: Optional[int] = None
    waste_increase_percent: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class EventOut(EventCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MultiMethodCalculationIn(BaseModel):
    location_id: Optional[int] = None
    habitation_id: Optional[int] = None
    population: float = Field(0.0, ge=0)
    waste_per_person_kg_day: float = Field(0.50, ge=0)
    households: float = Field(0.0, ge=0)
    waste_per_household_kg_day: float = Field(2.27, ge=0)
    measured_waste_tonnes_day: Optional[float] = Field(None, ge=0)
    measured_data_quality: str = "HIGH"
    industry_count: int = Field(0, ge=0)
    industry_workers: int = Field(0, ge=0)
    industry_worker_waste_kg_day: float = Field(0.60, ge=0)
    reported_industry_waste_kg_day: Optional[float] = Field(None, ge=0)
    hospital_beds: int = Field(0, ge=0)
    occupied_beds: int = Field(0, ge=0)
    hospital_waste_per_bed_kg_day: float = Field(1.50, ge=0)
    reported_hospital_waste_kg_day: Optional[float] = Field(None, ge=0)
    institution_students_staff: int = Field(0, ge=0)
    institution_waste_per_person_kg_day: float = Field(0.15, ge=0)
    reported_institution_waste_kg_day: Optional[float] = Field(None, ge=0)
    hotel_rooms: int = Field(0, ge=0)
    hotel_occupancy_rate: float = Field(0.70, ge=0, le=1.0)
    hotel_waste_per_guest_kg_day: float = Field(0.80, ge=0)
    reported_hotel_waste_kg_day: Optional[float] = Field(None, ge=0)
    market_vendors: int = Field(0, ge=0)
    market_waste_per_vendor_kg_day: float = Field(8.0, ge=0)
    reported_market_waste_kg_day: Optional[float] = Field(None, ge=0)
    floating_population: float = Field(0.0, ge=0)
    tourist_population: float = Field(0.0, ge=0)
    event_population: float = Field(0.0, ge=0)
    event_waste_percent: float = Field(0.0, ge=0, le=100.0)
    seasonal_factor: float = Field(1.0, ge=0.1, le=5.0)

class MultiMethodCalculationOut(BaseModel):
    method_a_person_based: Dict[str, Any]
    method_b_household_based: Dict[str, Any]
    method_c_measured_based: Optional[Dict[str, Any]] = None
    method_d_industry_based: Dict[str, Any]
    method_e_hospital_based: Dict[str, Any]
    method_f_institution_based: Dict[str, Any]
    method_g_hotel_based: Dict[str, Any]
    method_h_market_based: Dict[str, Any]
    source_aggregated: Dict[str, Any]
    cross_method_comparison: Dict[str, Any]
    reconciliation: Dict[str, Any]
