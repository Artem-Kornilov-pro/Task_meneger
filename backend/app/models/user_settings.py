# app/models/user_settings.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    timezone = Column(String(50), default="UTC")
    use_google_sync = Column(Boolean, default=False)

    user = relationship("User", back_populates="settings")
