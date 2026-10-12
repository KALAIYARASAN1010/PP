from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User
from ..schemas import Token, UserResponse, LoginRequest, UserCreate
from ..auth import verify_password, create_access_token, get_current_user, require_roles, hash_password
from ..audit import log_audit_event

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_req.username).first()
    if not user or not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect badge credentials or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )

    log_audit_event(
        db=db,
        user_name=user.username,
        action="USER_LOGIN",
        entity_type="Auth",
        entity_id=str(user.id),
        details={"username": user.username, "role": user.role, "badge": user.badge_number},
        user_id=user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# Also support standard OAuth2 form login for OpenAPI docs
@router.post("/token", response_model=Token)
def token_form_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login(LoginRequest(username=form_data.username, password=form_data.password), db)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Reviewer"]))
):
    return db.query(User).filter(User.is_active == True).all()
