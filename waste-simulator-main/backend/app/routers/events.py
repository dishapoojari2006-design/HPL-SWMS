from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.event import Event
from app.models.location import Location
from app.schemas.waste import EventCreate, EventUpdate, EventOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/events", tags=["Festivals & Cultural Events"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]
DELETE_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"]

@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, event_in.habitation_id):
        raise HTTPException(status_code=404, detail="Referenced location does not exist.")

    ev = Event(**event_in.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_EVENT",
        module="EVENTS",
        record_id=ev.id,
        details={"name": ev.name, "type": ev.event_type}
    )

    return ev

@router.get("", response_model=List[EventOut])
def list_events(
    habitation_id: Optional[int] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Event)
    if habitation_id is not None:
        query = query.where(Event.habitation_id == habitation_id)
    if event_type is not None:
        query = query.where(Event.event_type == event_type)
    return db.scalars(query.order_by(Event.id.asc())).all()

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")
    return ev

@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")

    update_data = event_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(ev, field, val)

    db.commit()
    db.refresh(ev)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="UPDATE_EVENT",
        module="EVENTS",
        record_id=ev.id,
        details=update_data
    )

    return ev

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*DELETE_ROLES))
):
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found.")

    db.delete(ev)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_EVENT",
        module="EVENTS",
        record_id=event_id,
        details={"name": ev.name}
    )
