from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.disaster import DisasterScenario
from app.schemas.disaster import DisasterScenarioCreate, DisasterScenarioOut, DisasterWhatIfRequest
from app.services.disaster_engine import run_disaster_what_if_analysis

router = APIRouter(prefix="/disaster-scenarios", tags=["Disaster Scenarios & What-If Planning"])

@router.get("", response_model=List[DisasterScenarioOut])
def list_disaster_scenarios(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(DisasterScenario)
    if location_id:
        query = query.where(DisasterScenario.location_id == location_id)
    return db.scalars(query).all()

@router.post("", response_model=DisasterScenarioOut, status_code=status.HTTP_201_CREATED)
def create_disaster_scenario(
    scen_in: DisasterScenarioCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    scen = DisasterScenario(
        location_id=scen_in.location_id,
        name=scen_in.name,
        disaster_type=scen_in.disaster_type,
        severity=scen_in.severity,
        duration_days=scen_in.duration_days,
        affected_population=scen_in.affected_population,
        displaced_population=scen_in.displaced_population,
        shelter_population=scen_in.shelter_population,
        road_access_pct=scen_in.road_access_pct,
        collection_efficiency_pct=scen_in.collection_efficiency_pct,
        treatment_capacity_pct=scen_in.treatment_capacity_pct,
        additional_waste_pct=scen_in.additional_waste_pct,
        debris_tonnes_day=scen_in.debris_tonnes_day,
        parameters=scen_in.parameters or {}
    )
    db.add(scen)
    db.commit()
    db.refresh(scen)
    return scen

@router.post("/what-if")
def disaster_what_if_analysis(
    req: DisasterWhatIfRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    base_params = {
        "normal_waste_tonnes_day": 12.5,
        "normal_fleet_capacity_tonnes_day": 20.0,
        "normal_treatment_capacity_tonnes_day": 10.0,
        "duration_days": req.baseline_scenario.duration_days,
        "affected_population": req.baseline_scenario.affected_population,
        "displaced_population": req.baseline_scenario.displaced_population,
        "shelter_population": req.baseline_scenario.shelter_population,
        "road_access_pct": req.baseline_scenario.road_access_pct,
        "collection_efficiency_pct": req.baseline_scenario.collection_efficiency_pct,
        "treatment_capacity_pct": req.baseline_scenario.treatment_capacity_pct,
        "additional_waste_pct": req.baseline_scenario.additional_waste_pct,
        "debris_tonnes_day": req.baseline_scenario.debris_tonnes_day
    }

    mod_params = {
        "normal_waste_tonnes_day": 12.5,
        "normal_fleet_capacity_tonnes_day": 20.0,
        "normal_treatment_capacity_tonnes_day": 10.0,
        "duration_days": req.modified_scenario.duration_days,
        "affected_population": req.modified_scenario.affected_population,
        "displaced_population": req.modified_scenario.displaced_population,
        "shelter_population": req.modified_scenario.shelter_population,
        "road_access_pct": req.modified_scenario.road_access_pct,
        "collection_efficiency_pct": req.modified_scenario.collection_efficiency_pct,
        "treatment_capacity_pct": req.modified_scenario.treatment_capacity_pct,
        "additional_waste_pct": req.modified_scenario.additional_waste_pct,
        "debris_tonnes_day": req.modified_scenario.debris_tonnes_day
    }

    return run_disaster_what_if_analysis(base_params, mod_params)
