from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.location import Location
from app.models.parameters import DemographyParameter, InfrastructureParameter
from app.models.disaster import DisasterEvent, DisasterImpact, DisasterDailyAnalysis
from app.schemas.disaster import DisasterEventCreate, DisasterEventOut, DisasterImpactIn, DisasterImpactOut
from app.services.audit_service import log_audit_event
from app.services.disaster_engine import run_disaster_multi_day_accumulation

router = APIRouter(prefix="/disasters", tags=["Disaster & Environmental Emergencies"])

@router.get("", response_model=List[DisasterEventOut])
@router.get("/events", response_model=List[DisasterEventOut])
def list_disaster_events(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(DisasterEvent)
    if location_id:
        query = query.where(DisasterEvent.location_id == location_id)
    return db.scalars(query).all()

@router.post("", response_model=DisasterEventOut, status_code=status.HTTP_201_CREATED)
def create_disaster_event(
    event_in: DisasterEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    loc = db.get(Location, event_in.location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location does not exist.")

    event = DisasterEvent(
        location_id=event_in.location_id,
        habitation_id=event_in.habitation_id,
        disaster_type=event_in.disaster_type,
        name=event_in.name,
        start_date=event_in.start_date,
        end_date=event_in.end_date,
        duration_days=event_in.duration_days,
        severity=event_in.severity,
        warning_level=event_in.warning_level,
        affected_area_sqkm=event_in.affected_area_sqkm,
        affected_population=event_in.affected_population,
        displaced_population=event_in.displaced_population,
        temporary_population=event_in.temporary_population,
        phase=event_in.phase,
        status=event_in.status,
        source=event_in.source,
        data_quality=event_in.data_quality,
        notes=event_in.notes,
        created_by=user.name
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Attach default impact factor profile
    impact = DisasterImpact(
        disaster_event_id=event.id,
        infrastructure_damage_factor=0.20 if event.severity in ["HIGH", "EXTREME"] else 0.10,
        road_access_factor=0.50 if event.severity in ["HIGH", "EXTREME"] else 0.75,
        collection_efficiency_factor=0.60 if event.severity in ["HIGH", "EXTREME"] else 0.80,
        treatment_capacity_factor=0.80,
        additional_waste_pct=25.0 if event.severity in ["HIGH", "EXTREME"] else 10.0,
        debris_factor=3.0 if event.severity in ["HIGH", "EXTREME"] else 1.0,
        notes="Standard initial impact profile"
    )
    db.add(impact)
    db.commit()
    db.refresh(event)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE",
        module="DISASTER",
        record_id=event.id,
        details={"disaster_type": event.disaster_type, "severity": event.severity, "name": event.name}
    )

    return event

@router.get("/{event_id}", response_model=DisasterEventOut)
def get_disaster_event(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    event = db.get(DisasterEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Disaster event record not found.")
    return event

@router.post("/{event_id}/impact", response_model=DisasterImpactOut)
def set_or_update_disaster_impact(
    event_id: int,
    impact_in: DisasterImpactIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    event = db.get(DisasterEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Disaster event record not found.")

    impact = db.scalar(select(DisasterImpact).where(DisasterImpact.disaster_event_id == event_id))
    if not impact:
        impact = DisasterImpact(disaster_event_id=event_id)
        db.add(impact)

    for field, val in impact_in.model_dump().items():
        setattr(impact, field, val)

    db.commit()
    db.refresh(impact)
    return impact

@router.post("/{event_id}/simulate")
def simulate_disaster_event(
    event_id: int,
    params: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    event = db.get(DisasterEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Disaster event record not found.")

    impact = db.scalar(select(DisasterImpact).where(DisasterImpact.disaster_event_id == event_id))
    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == event.location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == event.location_id))

    normal_pop = demo.total_population if demo else 25000.0
    per_cap = demo.waste_per_capita_kg if demo else 0.50
    normal_waste_tonnes = (params and params.get("nominal_daily_waste_tonnes")) or round((normal_pop * per_cap) / 1000.0, 3)

    fleet_vehicles = infra.vehicle_count if infra else 10
    vehicle_cap_kg = infra.vehicle_capacity_kg if infra else 2000.0
    trips = infra.trips_per_vehicle if infra else 1
    normal_fleet_cap_tonnes = round((fleet_vehicles * vehicle_cap_kg * trips) / 1000.0, 3)

    normal_treatment_cap_tonnes = round((infra.treatment_capacity_kg if infra else 10000.0) / 1000.0, 3)

    road_access_pct = (impact.road_access_factor * 100.0) if impact else 50.0
    collection_eff_pct = (impact.collection_efficiency_factor * 100.0) if impact else 60.0
    treatment_cap_pct = (impact.treatment_capacity_factor * 100.0) if impact else 80.0
    additional_waste_pct = impact.additional_waste_pct if impact else 25.0
    debris_tonnes_day = impact.debris_factor if impact else 2.5

    results = run_disaster_multi_day_accumulation(
        normal_waste_tonnes_day=normal_waste_tonnes,
        normal_fleet_capacity_tonnes_day=normal_fleet_cap_tonnes,
        normal_treatment_capacity_tonnes_day=normal_treatment_cap_tonnes,
        duration_days=event.duration_days,
        affected_population=event.affected_population,
        displaced_population=event.displaced_population,
        shelter_population=event.temporary_population,
        road_access_pct=road_access_pct,
        collection_efficiency_pct=collection_eff_pct,
        treatment_capacity_pct=treatment_cap_pct,
        additional_waste_pct=additional_waste_pct,
        debris_tonnes_day=debris_tonnes_day,
        start_date_val=event.start_date,
        vehicle_capacity_tonnes=vehicle_cap_kg / 1000.0,
        trips_per_vehicle=trips
    )

    return {
        "event_id": event.id,
        "event_name": event.name,
        "disaster_type": event.disaster_type,
        "severity": event.severity,
        "summary": {
            "total_period_generated_tonnes": results["total_period_generated_tonnes"],
            "total_period_collected_tonnes": results["total_period_collected_tonnes"],
            "total_period_uncollected_tonnes": results["total_period_uncollected_tonnes"],
            "peak_accumulated_tonnes": results["peak_accumulated_waste_tonnes"],
            "total_period_treated_tonnes": results["total_period_treated_tonnes"],
            "treatment_gap_tonnes": results["total_period_treatment_gap_tonnes"],
            "max_vehicle_deficit": results["max_vehicle_deficit"]
        },
        "daily_analysis": results["daily_series"]
    }

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disaster_event(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"))
):
    event = db.get(DisasterEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Disaster event not found.")
    db.delete(event)
    db.commit()
