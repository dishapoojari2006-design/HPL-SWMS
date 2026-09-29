from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import Report
from app.services.report_service import generate_comprehensive_report

router = APIRouter(prefix="/reports", tags=["Planning Reports"])

@router.get("/{location_id}")
def get_location_report(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        return generate_comprehensive_report(db=db, location_id=location_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{location_id}/publish")
def publish_report(
    location_id: int,
    title: str = "SWMS Official Municipal Waste Plan",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    report_data = generate_comprehensive_report(db=db, location_id=location_id)
    rep = Report(
        location_id=location_id,
        title=title,
        report_type="PUBLISHED_MASTER_PLAN",
        data=report_data
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return {"report_id": rep.id, "title": rep.title, "status": "Published"}
