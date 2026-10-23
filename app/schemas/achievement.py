from pydantic import BaseModel
from app.models.achievement import AchievementType
from datetime import datetime

class AchievementRead(BaseModel):
    created_at: datetime
    updated_at: datetime
    type: AchievementType

