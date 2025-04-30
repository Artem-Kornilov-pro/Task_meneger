from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(20), nullable=True)

    tasks = relationship("Task", back_populates="status")