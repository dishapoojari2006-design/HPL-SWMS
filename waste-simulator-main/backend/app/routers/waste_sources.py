from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.waste_source import WasteSource
from app.models.location import Location
from app.schemas.waste import WasteSourceCreate, WasteSourceUpdate, WasteSourceOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/waste-sources", tags=["Waste Sources"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]
DELETE_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"]

@router.post("", response_model=WasteSourceOut, status_code=status.HTTP_201_CREATED)
def create_waste_source(
    src_in: WasteSourceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, src_in.habitation_id):
        raise HTTPException(status_code=404, detail="Referenced habitation/location not found.")

    data = src_in.model_dump()
    if data["daily_waste_kg"] == 0 and data["units_count"] > 0 and data["rate_per_unit_kg_day"] > 0:
        data["daily_waste_kg"] = round(data["units_count"] * data["rate_per_unit_kg_day"], 2)

    src = WasteSource(**data)
    db.add(src)
    db.commit()
    db.refresh(src)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_WASTE_SOURCE",
        module="WASTE_SOURCES",
        record_id=src.id,
        details={"name": src.name, "type": src.source_type}
    )

    return src

@router.get("", response_model=List[WasteSourceOut])
def list_waste_sources(
    habitation_id: Optional[int] = None,
    source_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(WasteSource)
    if habitation_id is not None:
        query = query.where(WasteSource.habitation_id == habitation_id)
    if source_type is not None:
        query = query.where(WasteSource.source_type == source_type)
    return db.scalars(query.order_by(WasteSource.id.asc())).all()

@router.get("/{source_id}", response_model=WasteSourceOut)
def get_waste_source(
    source_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    src = db.get(WasteSource, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="Waste source not found.")
    return src

@router.put("/{source_id}", response_model=WasteSourceOut)
def update_waste_source(
    source_id: int,
    src_in: WasteSourceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    src = db.get(WasteSource, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="Waste source not found.")

    update_data = src_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(src, field, val)

    db.commit()
    db.refresh(src)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="UPDATE_WASTE_SOURCE",
        module="WASTE_SOURCES",
        record_id=src.id,
        details=update_data
    )

    return src

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waste_source(
    source_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*DELETE_ROLES))
):
    src = db.get(WasteSource, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="Waste source not found.")

    db.delete(src)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_WASTE_SOURCE",
        module="WASTE_SOURCES",
        record_id=source_id,
        details={"name": src.name}
    )
