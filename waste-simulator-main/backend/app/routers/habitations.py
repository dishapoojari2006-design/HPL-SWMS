from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.habitation import Habitation
from app.models.location import Location
from app.schemas.location import HabitationCreate, HabitationUpdate, HabitationOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/habitations", tags=["Habitations"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]
DELETE_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"]

@router.post("", response_model=HabitationOut, status_code=status.HTTP_201_CREATED)
def create_habitation(
    hab_in: HabitationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, hab_in.location_id):
        raise HTTPException(status_code=404, detail=f"Parent location ID {hab_in.location_id} does not exist.")

    hab = Habitation(**hab_in.model_dump())
    db.add(hab)
    db.commit()
    db.refresh(hab)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_HABITATION",
        module="HABITATIONS",
        record_id=hab.id,
        details={"name": hab.name, "location_id": hab.location_id}
    )

    return hab

@router.get("", response_model=List[HabitationOut])
def list_habitations(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Habitation)
    if location_id is not None:
        query = query.where(Habitation.location_id == location_id)
    return db.scalars(query.order_by(Habitation.id.asc())).all()

@router.get("/{habitation_id}", response_model=HabitationOut)
def get_habitation(
    habitation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    hab = db.get(Habitation, habitation_id)
    if not hab:
        raise HTTPException(status_code=404, detail=f"Habitation with ID {habitation_id} not found.")
    return hab

@router.put("/{habitation_id}", response_model=HabitationOut)
def update_habitation(
    habitation_id: int,
    hab_in: HabitationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    hab = db.get(Habitation, habitation_id)
    if not hab:
        raise HTTPException(status_code=404, detail=f"Habitation with ID {habitation_id} not found.")

    update_data = hab_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(hab, field, val)

    db.commit()
    db.refresh(hab)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="UPDATE_HABITATION",
        module="HABITATIONS",
        record_id=hab.id,
        details=update_data
    )

    return hab

@router.delete("/{habitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habitation(
    habitation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*DELETE_ROLES))
):
    hab = db.get(Habitation, habitation_id)
    if not hab:
        raise HTTPException(status_code=404, detail=f"Habitation with ID {habitation_id} not found.")

    db.delete(hab)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_HABITATION",
        module="HABITATIONS",
        record_id=habitation_id,
        details={"name": hab.name}
    )
