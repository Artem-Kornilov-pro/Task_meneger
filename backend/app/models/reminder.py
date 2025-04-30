from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    message = Column(String(255), nullable=True)

    task = relationship("Task", back_populates="reminders")
