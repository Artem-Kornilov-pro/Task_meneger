# app/models/task_category.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class TaskCategory(Base):
    __tablename__ = "task_categories"

    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)

    task = relationship("Task", back_populates="categories")
    category = relationship("Category", back_populates="task_links")
