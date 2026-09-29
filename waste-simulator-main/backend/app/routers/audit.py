from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.report import AuditLogOut

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogOut])
def get_audit_logs(
    module: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY"))
):
    query = select(AuditLog)
    if module:
        query = query.where(AuditLog.module == module)
    return db.scalars(query.order_by(AuditLog.timestamp.desc()).limit(limit)).all()
