from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from collections.abc import AsyncGenerator

DATABASE_URL = os.environ.get(
  "DATABASE_URL",
  "postgresql+asyncpg://andrey@localhost/dobox",
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
  pass


from collections.abc import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
  async with async_session() as session:
    try:
      yield session
    except Exception:
      await session.rollback()
      raise
