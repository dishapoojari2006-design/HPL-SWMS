from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import ConfigDict, BaseModel, Field

class ReportCreate(BaseModel):
    location_id: int
    title: str = Field(min_length=2, max_length=255)
    report_type: str = "MUNICIPAL_SUMMARY"
    data: Dict[str, Any] = Field(default_factory=dict)

class ReportOut(ReportCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: str
    action: str
    module: str
    record_id: Optional[int] = None
    details: Dict[str, Any]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
