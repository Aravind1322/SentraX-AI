"""
SentraX AI Backend — models/setting.py
SQLAlchemy Setting model.
"""

from sqlalchemy import Column, String
from database.base import Base


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
