"""
backend/routes/auth.py - Authentication REST API Endpoints
Endpoints:
- POST /api/register
- POST /api/login
- POST /api/logout
- GET /api/me
Logs every login attempt (success and failure) to the login_logs table.
Never exposes password hashes.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.database import get_db
from backend.models import User
from backend.auth import (
    hash_password,
    verify_password,
    create_session_token,
    get_client_ip,
    log_login_attempt,
    get_current_user
)

router = APIRouter(prefix="/api", tags=["Authentication"])


class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (at least 6 chars)")


class LoginSchema(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Password")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterSchema, request: Request, db: Session = Depends(get_db)):
    """
    Registers a new regular customer account.
    Validates input, checks uniqueness, hashes password, and logs initial activity.
    """
    email_clean = req.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Hash the password with bcrypt
    pw_hash = hash_password(req.password)

    new_user = User(
        name=req.name.strip(),
        email=email_clean,
        password_hash=pw_hash,
        role="user",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Also log a successful registration login event
    ip = get_client_ip(request)
    log_login_attempt(db, email=email_clean, ip_address=ip, status_str="success", user_id=new_user.id)

    # Generate token
    token = create_session_token(new_user.id, new_user.email, new_user.role)

    return {
        "message": "Registration successful.",
        "token": token,
        "user": new_user.to_dict()
    }


@router.post("/login")
def login(req: LoginSchema, request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates a user, logs the attempt (success or failure) to login_logs,
    and returns a session token + sets session_token cookie.
    """
    email_clean = req.email.strip().lower()
    ip = get_client_ip(request)

    # Find user by email
    user = db.query(User).filter(User.email == email_clean).first()

    # If user doesn't exist or password mismatch -> failed attempt
    if not user or not verify_password(req.password, user.password_hash):
        log_login_attempt(
            db,
            email=email_clean,
            ip_address=ip,
            status_str="failed",
            user_id=user.id if user else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Successful login
    log_login_attempt(
        db,
        email=email_clean,
        ip_address=ip,
        status_str="success",
        user_id=user.id
    )

    token = create_session_token(user.id, user.email, user.role)

    # Set cookie for easy browser session management
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=False,  # Accessible by vanilla JS if needed
        max_age=86400,
        samesite="lax",
        path="/"
    )

    return {
        "message": "Login successful.",
        "token": token,
        "user": user.to_dict()
    }


@router.post("/logout")
def logout(response: Response):
    """
    Logs out the user by clearing the session cookie.
    Client-side also removes token from localStorage.
    """
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully."}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns current authenticated user profile without password hash.
    """
    return {"user": current_user.to_dict()}
