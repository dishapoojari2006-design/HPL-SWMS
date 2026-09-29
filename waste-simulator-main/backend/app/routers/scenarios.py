from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.strategy_scenario import Scenario
from app.models.location import Location
from app.schemas.simulation import ScenarioCreate, ScenarioOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/scenarios", tags=["What-If Scenarios"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"]

@router.post("", response_model=ScenarioOut, status_code=status.HTTP_201_CREATED)
def create_scenario(
    scen_in: ScenarioCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, scen_in.location_id):
        raise HTTPException(status_code=404, detail="Referenced location does not exist.")

    scen = Scenario(**scen_in.model_dump())
    db.add(scen)
    db.commit()
    db.refresh(scen)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_SCENARIO",
        module="SCENARIOS",
        record_id=scen.id,
        details={"name": scen.name, "type": scen.scenario_type}
    )

    return scen

@router.get("", response_model=List[ScenarioOut])
def list_scenarios(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Scenario)
    if location_id is not None:
        query = query.where(Scenario.location_id == location_id)
    return db.scalars(query.order_by(Scenario.id.asc())).all()

@router.get("/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scen = db.get(Scenario, scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    return scen

@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*EDIT_ROLES))):
    scen = db.get(Scenario, scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    db.delete(scen)
    db.commit()
