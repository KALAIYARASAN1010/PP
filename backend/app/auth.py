import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def hash_password(password: str) -> str:
    """Generate salted SHA-256 password hash."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salted PBKDF2 hash."""
    try:
        salt, key_hex = hashed_password.split(":")
        new_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if username is None or role is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role, user_id=user_id)
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_roles(allowed_roles: List[str]):
    """Enforces Role-Based Access Control (RBAC). Returns 403 on violations."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {allowed_roles} roles. Your role is '{current_user.role}'."
            )
        return current_user
    return role_checker
