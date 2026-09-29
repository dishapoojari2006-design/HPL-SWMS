from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_audit_event(
    db: Session,
    user_name: str,
    action: str,
    module: str,
    record_id: Optional[int] = None,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        module=module,
        record_id=record_id,
        details=details or {},
        timestamp=datetime.now(timezone.utc)
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
