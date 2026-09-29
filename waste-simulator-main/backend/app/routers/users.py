from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, hash_password
from app.models.user import User
from app.schemas.auth import UserOut, UserUpdate, UserRegister
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("SUPER_ADMIN"))
):
    return db.scalars(select(User).order_by(User.id.asc())).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("SUPER_ADMIN"))
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("SUPER_ADMIN"))
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(user, field, val)

    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        user_name=admin.name,
        user_id=admin.id,
        action="UPDATE_USER",
        module="USERS",
        record_id=user.id,
        details=update_data
    )

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("SUPER_ADMIN"))
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own active administrator account")

    db.delete(user)
    db.commit()

    log_audit_event(
        db=db,
        user_name=admin.name,
        user_id=admin.id,
        action="DELETE_USER",
        module="USERS",
        record_id=user_id,
        details={"deleted_user_email": user.email}
    )
