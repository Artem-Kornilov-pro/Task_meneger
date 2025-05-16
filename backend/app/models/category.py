# /backend/app/models/category.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(20), nullable=True)

    task_links = relationship("TaskCategory", back_populates="category")

