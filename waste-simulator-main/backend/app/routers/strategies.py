from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.strategy_scenario import Strategy
from app.models.location import Location
from app.schemas.simulation import StrategyCreate, StrategyOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/strategies", tags=["Planning Strategies"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"]

@router.post("", response_model=StrategyOut, status_code=status.HTTP_201_CREATED)
def create_strategy(
    strat_in: StrategyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, strat_in.location_id):
        raise HTTPException(status_code=404, detail="Referenced location does not exist.")

    st = Strategy(**strat_in.model_dump())
    db.add(st)
    db.commit()
    db.refresh(st)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_STRATEGY",
        module="STRATEGIES",
        record_id=st.id,
        details={"name": st.name, "type": st.strategy_type}
    )

    return st

@router.get("", response_model=List[StrategyOut])
def list_strategies(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Strategy)
    if location_id is not None:
        query = query.where(Strategy.location_id == location_id)
    return db.scalars(query.order_by(Strategy.id.asc())).all()

@router.get("/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    st = db.get(Strategy, strategy_id)
    if not st:
        raise HTTPException(status_code=404, detail="Strategy not found.")
    return st

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(strategy_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*EDIT_ROLES))):
    st = db.get(Strategy, strategy_id)
    if not st:
        raise HTTPException(status_code=404, detail="Strategy not found.")
    db.delete(st)
    db.commit()
