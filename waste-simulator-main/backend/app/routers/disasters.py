from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.location import Location
from app.models.disaster import DisasterEvent, DisasterImpact
from app.schemas.disaster import DisasterEventCreate, DisasterEventOut, DisasterImpactIn, DisasterImpactOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/disasters", tags=["Disaster & Environmental Emergencies"])

@router.get("", response_model=List[DisasterEventOut])
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
