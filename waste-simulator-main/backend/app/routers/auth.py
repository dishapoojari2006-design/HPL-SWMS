from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == user_in.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )
    
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        authority_type=user_in.authority_type,
        organization=user_in.organization,
        location_id=user_in.location_id,
        active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="REGISTER",
        module="AUTH",
        record_id=user.id,
        details={"email": user.email, "role": user.role}
    )

    return user

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == login_in.email))
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password."
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated. Please contact your administrator."
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="LOGIN",
        module="AUTH",
        record_id=user.id,
        details={"email": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "authority_type": user.authority_type,
            "organization": user.organization,
            "location_id": user.location_id
        }
    }

@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user

@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"message": "Successfully signed out."}
