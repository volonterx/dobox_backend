from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement, AchievementType
from app.models.item import Item


async def award_achievements(db: AsyncSession, user_id: UUID) -> None:
  created = await db.scalar(
    select(func.count()).select_from(Item).where(Item.user_id == user_id)
  )
  if created >= 10:
    await db.execute(
      insert(Achievement)
      .values(user_id=user_id, type=AchievementType.TEN_CREATED)
      .on_conflict_do_nothing(constraint="uq_achievement_user_type")
    )