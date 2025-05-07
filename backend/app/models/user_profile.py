from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    full_name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    location = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=True)
    use_google_sync = Column(Boolean, default=False, nullable=True)

    user = relationship("User", back_populates="profile")
