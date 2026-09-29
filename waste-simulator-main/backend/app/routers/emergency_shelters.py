from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.disaster import EmergencyShelter
from app.schemas.disaster import EmergencyShelterCreate, EmergencyShelterOut

router = APIRouter(prefix="/emergency-shelters", tags=["Emergency Relief Shelters"])

@router.get("", response_model=List[EmergencyShelterOut])
def list_emergency_shelters(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(EmergencyShelter)
    if location_id:
        query = query.where(EmergencyShelter.location_id == location_id)
    return db.scalars(query).all()

@router.post("", response_model=EmergencyShelterOut, status_code=status.HTTP_201_CREATED)
def create_emergency_shelter(
    shelter_in: EmergencyShelterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    shelter = EmergencyShelter(
        location_id=shelter_in.location_id,
        name=shelter_in.name,
        shelter_code=shelter_in.shelter_code,
        capacity_persons=shelter_in.capacity_persons,
        current_population=shelter_in.current_population,
        waste_per_person_kg_day=shelter_in.waste_per_person_kg_day,
        latitude=shelter_in.latitude,
        longitude=shelter_in.longitude,
        start_date=shelter_in.start_date,
        end_date=shelter_in.end_date,
        status=shelter_in.status,
        source=shelter_in.source,
        notes=shelter_in.notes
    )
    db.add(shelter)
    db.commit()
    db.refresh(shelter)
    return shelter

@router.delete("/{shelter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency_shelter(
    shelter_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"))
):
    shelter = db.get(EmergencyShelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found.")
    db.delete(shelter)
    db.commit()
