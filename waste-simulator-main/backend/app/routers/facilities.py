from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.facility import Facility
from app.models.location import Location
from app.schemas.waste import FacilityCreate, FacilityUpdate, FacilityOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/facilities", tags=["Waste Facilities"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]
DELETE_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"]

@router.post("", response_model=FacilityOut, status_code=status.HTTP_201_CREATED)
def create_facility(
    fac_in: FacilityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, fac_in.location_id):
        raise HTTPException(status_code=404, detail="Referenced location does not exist.")

    fac = Facility(**fac_in.model_dump())
    db.add(fac)
    db.commit()
    db.refresh(fac)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_FACILITY",
        module="FACILITIES",
        record_id=fac.id,
        details={"name": fac.name, "type": fac.facility_type, "capacity": fac.capacity_kg_day}
    )

    return fac

@router.get("", response_model=List[FacilityOut])
def list_facilities(
    location_id: Optional[int] = None,
    facility_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Facility)
    if location_id is not None:
        query = query.where(Facility.location_id == location_id)
    if facility_type is not None:
        query = query.where(Facility.facility_type == facility_type)
    return db.scalars(query.order_by(Facility.id.asc())).all()

@router.get("/{facility_id}", response_model=FacilityOut)
def get_facility(facility_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    fac = db.get(Facility, facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found.")
    return fac

@router.put("/{facility_id}", response_model=FacilityOut)
def update_facility(
    facility_id: int,
    fac_in: FacilityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    fac = db.get(Facility, facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found.")

    update_data = fac_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(fac, field, val)

    db.commit()
    db.refresh(fac)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="UPDATE_FACILITY",
        module="FACILITIES",
        record_id=fac.id,
        details=update_data
    )

    return fac

@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(
    facility_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*DELETE_ROLES))
):
    fac = db.get(Facility, facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found.")

    db.delete(fac)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_FACILITY",
        module="FACILITIES",
        record_id=facility_id,
        details={"name": fac.name}
    )
