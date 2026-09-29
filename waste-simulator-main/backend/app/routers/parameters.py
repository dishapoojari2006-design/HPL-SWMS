from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.location import Location
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.schemas.parameters import (
    DemographyIn, DemographyOut,
    InfrastructureIn, InfrastructureOut,
    IndustrialIn, IndustrialOut,
    CompositionIn, CompositionOut
)
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/parameters", tags=["Planning Parameters"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]

@router.post("/demography", response_model=DemographyOut, status_code=status.HTTP_201_CREATED)
def save_demography(
    params_in: DemographyIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    existing = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == params_in.habitation_id))
    if existing:
        for k, v in params_in.model_dump().items():
            setattr(existing, k, v)
        row = existing
    else:
        row = DemographyParameter(**params_in.model_dump())
        db.add(row)

    db.commit()
    db.refresh(row)
    return row

@router.get("/demography/{habitation_id}", response_model=Optional[DemographyOut])
def get_demography(habitation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == habitation_id))
    if not row:
        raise HTTPException(status_code=404, detail="Demography parameters not found for this location.")
    return row

@router.post("/infrastructure", response_model=InfrastructureOut, status_code=status.HTTP_201_CREATED)
def save_infrastructure(
    params_in: InfrastructureIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    existing = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == params_in.habitation_id))
    if existing:
        for k, v in params_in.model_dump().items():
            setattr(existing, k, v)
        row = existing
    else:
        row = InfrastructureParameter(**params_in.model_dump())
        db.add(row)

    db.commit()
    db.refresh(row)
    return row

@router.get("/infrastructure/{habitation_id}", response_model=Optional[InfrastructureOut])
def get_infrastructure(habitation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == habitation_id))
    if not row:
        raise HTTPException(status_code=404, detail="Infrastructure parameters not found for this location.")
    return row

@router.post("/industrial", response_model=IndustrialOut, status_code=status.HTTP_201_CREATED)
def save_industrial(
    params_in: IndustrialIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    existing = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == params_in.habitation_id))
    if existing:
        for k, v in params_in.model_dump().items():
            setattr(existing, k, v)
        row = existing
    else:
        row = IndustrialParameter(**params_in.model_dump())
        db.add(row)

    db.commit()
    db.refresh(row)
    return row

@router.get("/industrial/{habitation_id}", response_model=Optional[IndustrialOut])
def get_industrial(habitation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == habitation_id))
    if not row:
        raise HTTPException(status_code=404, detail="Industrial parameters not found for this location.")
    return row

@router.post("/composition", response_model=CompositionOut, status_code=status.HTTP_201_CREATED)
def save_composition(
    params_in: CompositionIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    existing = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == params_in.habitation_id))
    if existing:
        for k, v in params_in.model_dump().items():
            setattr(existing, k, v)
        row = existing
    else:
        row = WasteComposition(**params_in.model_dump())
        db.add(row)

    db.commit()
    db.refresh(row)
    return row

@router.get("/composition/{habitation_id}", response_model=Optional[CompositionOut])
def get_composition(habitation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == habitation_id))
    if not row:
        raise HTTPException(status_code=404, detail="Waste composition not found for this location.")
    return row

@router.get("/summary/{habitation_id}")
def get_parameters_summary(habitation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    loc = db.get(Location, habitation_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found.")
        
    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == habitation_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == habitation_id))
    ind = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == habitation_id))
    comp = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == habitation_id))

    return {
        "location": {"id": loc.id, "name": loc.name, "type": loc.location_type, "terrain": loc.terrain, "classification": loc.classification},
        "demography": demo.__dict__ if demo else None,
        "infrastructure": infra.__dict__ if infra else None,
        "industrial": ind.__dict__ if ind else None,
        "composition": comp.__dict__ if comp else None
    }
