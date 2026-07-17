"""
SentraX AI Backend — utils/security.py
JWT creation, validation, password hashing, and role-based access helpers.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_connection

security_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = "changeme-before-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Securely hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    """Generate a JWT access token valid for short duration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Generate a JWT refresh token valid for long duration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# ── Dependency injection helpers for FastAPI routes ───────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and validate the authenticated user.
    If no authorization header is provided, it falls back to an anonymous viewer/analyst context
    to preserve 100% compatibility with the existing Streamlit frontend.
    """
    raw_token = credentials.credentials if credentials else None

    # 1. Fallback for anonymous Streamlit calls to preserve compatibility
    if not credentials or not raw_token:
        return {
            "id": None,
            "email": "anonymous@sentrax.ai",
            "full_name": "Anonymous Analyst",
            "role": "Anonymous Analyst",  # Grant Anonymous Analyst permissions by default
            "is_anonymous": True
        }

    token = raw_token

    # 2. Decode & Validate Token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject info"
        )

    # 4. Query user from SQLite
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_name, email, role, is_active FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account not found"
                )
            if not row["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated"
                )

            return {
                "id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "role": row["role"],
                "is_anonymous": False
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database validation error: {str(e)}"
        )


class RoleChecker:
    """Dependency helper to enforce Role Based Access Control (RBAC)."""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        user_role = current_user.get("role", "Anonymous Analyst")

        # Explicit direct hierarchy validation:
        # - Administrator passes Administrator, Security Analyst, Viewer, and Anonymous Analyst
        # - Security Analyst passes Security Analyst, Viewer, and Anonymous Analyst
        # - Viewer passes Viewer and Anonymous Analyst
        # - Anonymous Analyst passes Anonymous Analyst only
        role_permissions = {
            "Administrator": {"Administrator", "Security Analyst", "Viewer", "Anonymous Analyst"},
            "Security Analyst": {"Security Analyst", "Viewer", "Anonymous Analyst"},
            "Viewer": {"Viewer", "Anonymous Analyst"},
            "Anonymous Analyst": {"Anonymous Analyst"}
        }

        user_allowed_targets = role_permissions.get(user_role, {"Anonymous Analyst"})

        if any(r in user_allowed_targets for r in self.allowed_roles):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action"
        )
