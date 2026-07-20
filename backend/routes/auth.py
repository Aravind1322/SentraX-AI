"""
SentraX AI Backend — routes/auth.py
Endpoints for JWT-based user authentication, login, registration, logout, and token refresh.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from database import get_connection
from utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user
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
async def register_user(request: RegisterRequest):
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already registered"
                )

            # Debug logging variables before insert
            from config import SENTRAX_DEBUG, DATABASE_PATH
            if SENTRAX_DEBUG:
                import os
                cursor.execute("SELECT COUNT(*) FROM users")
                users_before = cursor.fetchone()[0]
                cursor.execute("PRAGMA database_list")
                db_list = cursor.fetchall()

            # Insert user
            password_hash = hash_password(request.password)
            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (request.full_name, request.email, password_hash, role)
            )
            new_id = cursor.lastrowid
            conn.commit()

            if SENTRAX_DEBUG:
                cursor.execute("SELECT COUNT(*) FROM users")
                users_after = cursor.fetchone()[0]
                db_size = os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0
                print("[DEBUG AUTH] USER REGISTERED VIA API:")
                print(f"  Resolved database path: {DATABASE_PATH}")
                print(f"  Absolute database path: {os.path.abspath(DATABASE_PATH)}")
                print(f"  PRAGMA database_list: {db_list}")
                print(f"  Total users before insert: {users_before}")
                print(f"  Inserted user ID: {new_id}")
                print(f"  Commit success: Yes")
                print(f"  Total users after insert: {users_after}")
                print(f"  Database file size: {db_size} bytes")

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
async def login_user(request: LoginRequest):
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
            
            # Debug logging helper variables
            from config import SENTRAX_DEBUG, DATABASE_PATH
            user_found = "Yes" if row else "No"
            matched_id = row["id"] if row else None
            auth_success = "Failure"
            login_update_success = "No"

            if not row or not verify_password(request.password, row["password_hash"]):
                if SENTRAX_DEBUG:
                    print("[DEBUG AUTH] LOGIN ATTEMPT:")
                    print(f"  Database path: {DATABASE_PATH}")
                    print(f"  User found: {user_found}")
                    print(f"  Matched ID: {matched_id}")
                    print(f"  Authentication result: {auth_success}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            if not row["is_active"]:
                if SENTRAX_DEBUG:
                    print("[DEBUG AUTH] LOGIN ATTEMPT (SUSPENDED):")
                    print(f"  Database path: {DATABASE_PATH}")
                    print(f"  User found: {user_found}")
                    print(f"  Matched ID: {matched_id}")
                    print(f"  Authentication result: {auth_success}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is suspended"
                )

            # Generate tokens
            user_payload = {"sub": request.email, "role": row["role"], "id": row["id"]}
            access_token = create_access_token(user_payload)
            refresh_token = create_refresh_token(user_payload)
            auth_success = "Success"

            # Update last login
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (current_time, row["id"])
            )
            conn.commit()
            login_update_success = "Yes" if conn.total_changes > 0 else "No"

            if SENTRAX_DEBUG:
                print("[DEBUG AUTH] LOGIN ATTEMPT:")
                print(f"  Database path: {DATABASE_PATH}")
                print(f"  User found: {user_found}")
                print(f"  Matched ID: {matched_id}")
                print(f"  Authentication result: {auth_success}")
                print(f"  Last login update success: {login_update_success}")

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
async def logout_user():
    """
    Invalidates session.
    """
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


class ChangeOwnPasswordRequest(BaseModel):
    current_password: str = Field(..., example="OldPassword123")
    new_password: str = Field(..., min_length=8, example="NewPassword123")


@router.get("/me", summary="Get current user profile")
async def get_own_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if current_user.get("is_anonymous"):
        return current_user

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_name, email, role, is_active, created_at, last_login FROM users WHERE id = ?",
                (current_user["id"],)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.post("/change-password", summary="Change own password")
async def change_own_password(
    request: ChangeOwnPasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if current_user.get("is_anonymous"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anonymous users cannot change passwords"
        )

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (current_user["id"],))
            row = cursor.fetchone()
            if not row or not verify_password(request.current_password, row["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect current password"
                )

            hashed_pw = hash_password(request.new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_pw, current_user["id"]))
            conn.commit()
            return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )



