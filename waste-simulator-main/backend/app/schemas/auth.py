from datetime import datetime
from typing import Optional, Literal
from pydantic import ConfigDict, BaseModel, EmailStr, Field

RoleType = Literal[
    "SUPER_ADMIN",
    "MUNICIPAL_AUTHORITY",
    "PANCHAYAT_AUTHORITY",
    "PLANNER",
    "DATA_ENTRY",
    "VIEWER"
]

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=30)
    role: RoleType = "VIEWER"
    authority_type: str = "OTHER"
    organization: Optional[str] = None
    location_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    authority_type: str
    organization: Optional[str] = None
    location_id: Optional[int] = None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[RoleType] = None
    authority_type: Optional[str] = None
    organization: Optional[str] = None
    location_id: Optional[int] = None
    active: Optional[bool] = None
