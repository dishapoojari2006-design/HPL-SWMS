from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate, LocationOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/locations", tags=["Locations Hierarchy"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]
DELETE_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"]

@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    loc_in: LocationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    loc = Location(**loc_in.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_LOCATION",
        module="LOCATIONS",
        record_id=loc.id,
        details={"name": loc.name, "type": loc.location_type}
    )

    return loc

@router.get("", response_model=List[LocationOut])
def list_locations(
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Location)
    if parent_id is not None:
        query = query.where(Location.parent_id == parent_id)
    return db.scalars(query.order_by(Location.id.asc())).all()

@router.get("/{location_id}", response_model=LocationOut)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found.")
    return loc

@router.put("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: int,
    loc_in: LocationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found.")

    update_data = loc_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(loc, field, val)

    db.commit()
    db.refresh(loc)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="UPDATE_LOCATION",
        module="LOCATIONS",
        record_id=loc.id,
        details=update_data
    )

    return loc

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*DELETE_ROLES))
):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found.")

    db.delete(loc)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_LOCATION",
        module="LOCATIONS",
        record_id=location_id,
        details={"name": loc.name}
    )
