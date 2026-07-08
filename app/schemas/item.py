from datetime import datetime

from pydantic import BaseModel

class ItemRead(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ItemCreate(BaseModel):
    title: str
    completed: bool | None = None

class ItemUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
