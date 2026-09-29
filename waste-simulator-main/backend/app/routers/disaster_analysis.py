from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.parameters import DemographyParameter, InfrastructureParameter
from app.schemas.disaster import DisasterAnalysisRequest
from app.services.disaster_engine import run_disaster_multi_day_accumulation, calculate_disaster_waste_components
from app.services.emergency_waste_service import estimate_disaster_debris_breakdown

router = APIRouter(prefix="/disaster-analysis", tags=["Disaster Impact & Accumulation Engine"])

@router.post("/simulate")
def simulate_disaster_accumulation(
    req: DisasterAnalysisRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == req.location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == req.location_id))

    pop = demo.total_population if demo else 25000.0
    per_capita = demo.waste_per_capita_kg if demo else 0.50
    normal_waste_tonnes = round((pop * per_capita) / 1000.0, 3)

    fleet_vehicles = infra.vehicle_count if infra else 10
    vehicle_cap_kg = infra.vehicle_capacity_kg if infra else 2000.0
    trips = infra.trips_per_vehicle if infra else 1
    normal_fleet_cap_tonnes = round((fleet_vehicles * vehicle_cap_kg * trips) / 1000.0, 3)

    normal_treatment_cap_tonnes = round((infra.treatment_capacity_kg if infra else 10000.0) / 1000.0, 3)

    debris_detail = estimate_disaster_debris_breakdown(
        disaster_type=req.disaster_type,
        severity=req.severity,
        affected_area_sqkm=15.0,
        affected_population=req.affected_population
    )

    actual_debris_tonnes = debris_detail["total_debris_tonnes_day"] if req.debris_tonnes_day <= 0 else req.debris_tonnes_day

    results = run_disaster_multi_day_accumulation(
        normal_waste_tonnes_day=normal_waste_tonnes,
        normal_fleet_capacity_tonnes_day=normal_fleet_cap_tonnes,
        normal_treatment_capacity_tonnes_day=normal_treatment_cap_tonnes,
        duration_days=req.duration_days,
        affected_population=req.affected_population,
        displaced_population=req.displaced_population,
        shelter_population=req.shelter_population,
        road_access_pct=req.road_access_pct,
        collection_efficiency_pct=req.collection_efficiency_pct,
        treatment_capacity_pct=req.treatment_capacity_pct,
        additional_waste_pct=req.additional_waste_pct,
        debris_tonnes_day=actual_debris_tonnes,
        vehicle_capacity_tonnes=vehicle_cap_kg / 1000.0,
        trips_per_vehicle=trips
    )

    results["debris_classification"] = debris_detail
    results["location_id"] = req.location_id
    results["disaster_type"] = req.disaster_type
    results["severity"] = req.severity

    return results

@router.get("/debris-profile")
def get_debris_profile(
    disaster_type: str = "Flood",
    severity: str = "HIGH",
    affected_area_sqkm: float = 15.0,
    affected_population: float = 5000.0,
    user: User = Depends(get_current_user)
):
    return estimate_disaster_debris_breakdown(
        disaster_type=disaster_type,
        severity=severity,
        affected_area_sqkm=affected_area_sqkm,
        affected_population=affected_population
    )
