from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TaskBase(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: Optional[str] = Field(None, example="Milk, Bread, Eggs")
    due_date: datetime = Field(None, example="2025-05-10T15:00:00")



class TaskCreate(TaskBase):
    status_id: Optional[Literal[1, 2, 3, 4]] = None

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    status_id: Optional[Literal[1, 2, 3, 4]] = None
    

class TaskOut(TaskBase):
    id: int
    user_id: int
    status_id: Optional[Literal[1, 2, 3, 4]] = None

    model_config = {
        "from_attributes": True
    }
