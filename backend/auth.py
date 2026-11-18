"""
backend/auth.py - Authentication and Security Utilities
Handles password hashing (bcrypt), JWT session tokens, login auditing,
and FastAPI authentication dependencies (get_current_user, get_current_admin).
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, LoginLog

# Secret configuration (can be overridden via environment variables)
SECRET_KEY = os.getenv("SECRET_KEY", "transport-secure-secret-key-2026-viva-demo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_session_token(user_id: int, email: str, role: str) -> str:
    """Generate a signed JWT session token with 24h expiration."""
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_session_token(token: str) -> Optional[dict]:
    """Decode and validate a signed JWT session token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def get_client_ip(request: Request) -> str:
    """Extract client IP address, respecting X-Forwarded-For if behind a proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First IP in comma-separated list is client IP
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def log_login_attempt(
    db: Session,
    email: str,
    ip_address: str,
    status_str: str,
    user_id: Optional[int] = None
) -> LoginLog:
    """
    Log every authentication attempt (success or failed) to the login_logs table.
    This directly updates the Admin Database Monitor.
    """
    try:
        log_entry = LoginLog(
            user_id=user_id,
            email_tried=email,
            login_time=datetime.now(timezone.utc),
            ip_address=ip_address,
            status=status_str  # 'success' or 'failed'
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        print(f"[AUTH ERROR] Failed to log login attempt: {e}")
        return None


def get_current_user(
    request: Request,
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts session token from either:
    1. Authorization: Bearer <token> header
    2. 'session_token' cookie
    Returns the authenticated User OR raises 401 Unauthorized.
    """
    token = None
    if bearer and bearer.credentials:
        token = bearer.credentials
    elif "session_token" in request.cookies:
        token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_session_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed session token."
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User belonging to this token no longer exists."
        )

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifies that the current user has role == 'admin'.
    Raises 403 Forbidden otherwise.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You do not have permission to view this resource."
        )
    return current_user
