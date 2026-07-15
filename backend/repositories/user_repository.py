"""
SentraX AI Backend — repositories/user_repository.py
Repository class abstraction for users using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.user import User
from typing import Optional


class UserRepository:
    """
    Handles all queries and writes targeting user profiles and roles.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user profile record matching specified email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch user profile record matching primary key."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, full_name: str, email: str, password_hash: str, role: str) -> User:
        """Create and persist a new user profile record."""
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        return user

    def count(self) -> int:
        """Count total registered user profiles in database."""
        return self.db.query(User).count()
