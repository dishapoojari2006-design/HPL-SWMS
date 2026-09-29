from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatIn(BaseModel):
    location_id: int
    question: str = Field(min_length=2, max_length=500)

class ChatOut(BaseModel):
    answer: str
    evidence: Dict[str, Any]
    source_attribution: str
    data_status: str
    created_at: datetime
