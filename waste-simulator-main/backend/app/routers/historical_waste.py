from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.historical_waste import HistoricalWaste
from app.models.location import Location
from app.schemas.historical_waste import (
    HistoricalWasteCreate,
    HistoricalWasteBulkCreate,
    HistoricalWasteOut,
    HistoricalPeriodAnalysisOut
)
from app.services.time_series_service import analyze_time_series_records
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/historical-waste", tags=["Historical Waste Time-Series"])

EDIT_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"]

@router.post("", response_model=HistoricalWasteOut, status_code=status.HTTP_201_CREATED)
def create_historical_record(
    record_in: HistoricalWasteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    if not db.get(Location, record_in.habitation_id):
        raise HTTPException(status_code=404, detail="Referenced location/habitation does not exist.")

    dup_query = select(HistoricalWaste).where(
        HistoricalWaste.habitation_id == record_in.habitation_id,
        HistoricalWaste.measurement_date == record_in.measurement_date,
        HistoricalWaste.source_id == record_in.source_id
    )
    if db.scalar(dup_query):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate entry: A record for date {record_in.measurement_date.isoformat()} already exists for this habitation and source."
        )

    rec = HistoricalWaste(**record_in.model_dump(), created_by=user.name)
    db.add(rec)
    db.commit()
    db.refresh(rec)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="CREATE_HISTORICAL_RECORD",
        module="HISTORICAL_WASTE",
        record_id=rec.id,
        details={"date": str(rec.measurement_date), "quantity": rec.quantity}
    )

    return rec

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_records(
    bulk_in: HistoricalWasteBulkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*EDIT_ROLES))
):
    created_count = 0
    duplicate_count = 0
    invalid_count = 0
    errors = []

    for r in bulk_in.records:
        if r.quantity < 0:
            invalid_count += 1
            errors.append(f"Negative waste quantity {r.quantity} on {r.measurement_date}")
            continue

        existing = db.scalar(
            select(HistoricalWaste).where(
                HistoricalWaste.habitation_id == r.habitation_id,
                HistoricalWaste.measurement_date == r.measurement_date,
                HistoricalWaste.source_id == r.source_id
            )
        )
        if existing:
            duplicate_count += 1
            continue

        rec = HistoricalWaste(**r.model_dump(), created_by=user.name)
        db.add(rec)
        created_count += 1

    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="BULK_IMPORT_HISTORICAL",
        module="HISTORICAL_WASTE",
        details={"created": created_count, "duplicates": duplicate_count, "invalid": invalid_count}
    )

    return {
        "summary": f"{len(bulk_in.records)} rows processed: {created_count} created, {duplicate_count} duplicates skipped, {invalid_count} invalid records.",
        "created_count": created_count,
        "duplicate_count": duplicate_count,
        "invalid_count": invalid_count,
        "errors": errors[:10]
    }

@router.get("", response_model=List[HistoricalWasteOut])
def list_records(
    habitation_id: int,
    period_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(HistoricalWaste).where(HistoricalWaste.habitation_id == habitation_id)
    if period_type:
        query = query.where(HistoricalWaste.period_type == period_type)
    if start_date:
        query = query.where(HistoricalWaste.measurement_date >= start_date)
    if end_date:
        query = query.where(HistoricalWaste.measurement_date <= end_date)

    return db.scalars(query.order_by(HistoricalWaste.measurement_date.asc())).all()

@router.get("/analytics", response_model=HistoricalPeriodAnalysisOut)
def get_analytics(
    habitation_id: int,
    period_type: str = Query("ALL", description="1_DAY, 2_DAYS, 1_WEEK, 1_MONTH, 3_MONTHS, 6_MONTHS, 1_YEAR, 2_YEARS, CUSTOM"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(HistoricalWaste).where(HistoricalWaste.habitation_id == habitation_id)
    if start_date:
        query = query.where(HistoricalWaste.measurement_date >= start_date)
    if end_date:
        query = query.where(HistoricalWaste.measurement_date <= end_date)

    records = db.scalars(query.order_by(HistoricalWaste.measurement_date.asc())).all()
    record_dicts = [{
        "measurement_date": r.measurement_date,
        "quantity": r.quantity,
        "waste_category": r.waste_category,
        "quality_status": r.quality_status
    } for r in records]

    return analyze_time_series_records(
        records=record_dicts,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date
    )

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    rec = db.get(HistoricalWaste, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Historical record not found.")

    db.delete(rec)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="DELETE_HISTORICAL_RECORD",
        module="HISTORICAL_WASTE",
        record_id=record_id
    )
