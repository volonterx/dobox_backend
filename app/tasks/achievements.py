import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database import DATABASE_URL
from app.services.achievements import award_achievements
from app.worker import celery_app

@celery_app.task
def check_achievements(user_id: str) -> None:
    asyncio.run(_award_for_user(UUID(user_id)))

async def _award_for_user(user_id: UUID) -> None:
    engine = create_async_engine(DATABASE_URL, pool_size=1, max_overflow=0)
    try:
        async with AsyncSession(engine) as db:
            await award_achievements(db, user_id)
            await db.commit()
    finally:
        await engine.dispose()
