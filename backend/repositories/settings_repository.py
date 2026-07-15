"""
SentraX AI Backend — repositories/settings_repository.py
Repository class abstraction for settings using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.setting import Setting
from typing import Dict, Any, Optional


class SettingsRepository:
    """
    Handles all queries and writes targeting global SOC settings.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[str]:
        """Fetch setting value associated with specified key name."""
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        return setting.value if setting else None

    def set(self, key: str, value: str) -> None:
        """Create or update setting record value key."""
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            self.db.add(Setting(key=key, value=value))
        self.db.commit()
