from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints, AfterValidator

Title = Annotated[str,
  StringConstraints(min_length=1, strip_whitespace=True),
  AfterValidator(lambda v: v.strip())
]

class ItemId(BaseModel):
  id: int

class ParentItemRead(BaseModel):
  id: int
  title: Title
  created_at: datetime
  updated_at: datetime
  started_at: datetime | None
  completed_at: datetime | None

  model_config = {"from_attributes": True}

class ItemRead(BaseModel):
  id: int
  title: Title
  created_at: datetime
  updated_at: datetime
  started_at: datetime | None
  completed_at: datetime | None
  parent: ParentItemRead | None

  model_config = {"from_attributes": True}

class ItemCreate(BaseModel):
  title: Title
  parent_id: int | None = None

class ItemUpdate(BaseModel):
  title: Title | None = None
  started_at: datetime | None = None
  completed: bool | None = None
  started: bool | None = None
  parent_id: int | None = None