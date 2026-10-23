from app.database import Base
from app.utils import utcnow
from enum import StrEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint, DateTime, ForeignKey, Enum
from datetime import datetime
from uuid import UUID


class AchievementType(StrEnum):
    TEN_DONE = "ten_done"
    TEN_CREATED = "ten_created"

class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "type", name="uq_achievement_user_type",
            info={"msg": "Achievement already granted"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[AchievementType] = mapped_column(Enum(AchievementType, native_enum=False, length=50))


