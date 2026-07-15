"""
SentraX AI Backend — routes/auth.py
Endpoints for JWT-based user authentication, login, registration, logout, and token refresh.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from database import get_connection, log_audit
from utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)

router = APIRouter()


class RegisterRequest(BaseModel):
    full_name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john.doe@sentrax.ai")
    password: str = Field(..., min_length=8, example="mypassword")
    role: str = Field("Security Analyst", example="Security Analyst")  # Viewer, Security Analyst, Administrator


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@sentrax.ai")
    password: str = Field(..., example="admin")


class TokenRefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", summary="Register a new enterprise user")
async def register_user(request: RegisterRequest, req_meta: Request):
    """
    Creates a new multi-user profile with secure bcrypt password hashing.
    By default, registers users under Security Analyst role.
    """
    role = request.role
    if role not in ["Administrator", "Security Analyst", "Viewer"]:
        role = "Security Analyst"

    try:
        # Check if email exists
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
            if cursor.fetchone():
                log_audit("auth_fail", f"Registration failed: email {request.email} already exists", ip_address=req_meta.client.host)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already registered"
                )

            # Insert user
            password_hash = hash_password(request.password)
            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (request.full_name, request.email, password_hash, role)
            )
            conn.commit()
            
            user_id = cursor.lastrowid
            log_audit("user_registration", f"Created user {request.email} with role {role}", user_id=user_id, ip_address=req_meta.client.host)

            return {
                "message": "User registered successfully",
                "email": request.email,
                "role": role
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", summary="Login to obtain access and refresh tokens")
async def login_user(request: LoginRequest, req_meta: Request):
    """
    Authenticates email & password. Returns short-lived access token and
    long-lived refresh token.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_name, password_hash, role, is_active FROM users WHERE email = ?",
                (request.email,)
            )
            row = cursor.fetchone()
            if not row or not verify_password(request.password, row["password_hash"]):
                log_audit("auth_fail", f"Failed login attempt for email {request.email}", ip_address=req_meta.client.host)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            if not row["is_active"]:
                log_audit("auth_fail", f"Suspended account login attempt: {request.email}", user_id=row["id"], ip_address=req_meta.client.host)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is suspended"
                )

            # Generate tokens
            user_payload = {"sub": request.email, "role": row["role"], "id": row["id"]}
            access_token = create_access_token(user_payload)
            refresh_token = create_refresh_token(user_payload)

            # Update last login
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (current_time, row["id"])
            )
            conn.commit()

            log_audit("login", f"Successful login for {request.email}", user_id=row["id"], ip_address=req_meta.client.host)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "email": request.email,
                    "full_name": row["full_name"],
                    "role": row["role"]
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout", summary="Logout user")
async def logout_user(req_meta: Request):
    """
    Invalidates session and logs logout action to the audit logs.
    """
    log_audit("logout", "User session ended", ip_address=req_meta.client.host)
    return {"message": "Logged out successfully"}


@router.post("/refresh", summary="Obtain a new access token using a refresh token")
async def refresh_token(request: TokenRefreshRequest):
    """
    Verifies the refresh token and generates a new access token.
    """
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    email = payload.get("sub")
    role = payload.get("role")
    user_id = payload.get("id")

    # Generate new access token
    new_payload = {"sub": email, "role": role, "id": user_id}
    access_token = create_access_token(new_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
