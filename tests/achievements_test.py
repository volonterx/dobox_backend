import pytest
from sqlalchemy import func, select

from app.models.achievement import Achievement, AchievementType
from app.models.item import Item
from app.services.achievements import award_achievements
from app.tasks.achievements import _award_for_user
from tests.conftest import TEST_DATABASE_URL, TestSession, create_user


async def add_items(user, count: int) -> None:
  async with TestSession() as db:
    db.add_all(Item(title=f"Task {i}", user_id=user.id) for i in range(count))
    await db.commit()


async def count_achievements() -> int:
  async with TestSession() as db:
    return await db.scalar(select(func.count()).select_from(Achievement))


async def run_service(user) -> None:
  async with TestSession() as db:
    await award_achievements(db, user.id)
    await db.commit()


@pytest.mark.asyncio
async def test_no_achievement_below_ten_items(user):
  await add_items(user, 9)

  await run_service(user)

  assert await count_achievements() == 0


@pytest.mark.asyncio
async def test_ten_items_award_ten_created(user):
  await add_items(user, 10)

  await run_service(user)

  async with TestSession() as db:
    achievement = (await db.execute(select(Achievement))).scalar_one()
  assert achievement.user_id == user.id
  assert achievement.type == AchievementType.TEN_CREATED


@pytest.mark.asyncio
async def test_running_twice_awards_once(user):
  await add_items(user, 10)

  await run_service(user)
  await run_service(user)

  assert await count_achievements() == 1


@pytest.mark.asyncio
async def test_only_counts_own_items(user):
  other = await create_user("bob@example.com")
  await add_items(other, 10)

  await run_service(user)

  assert await count_achievements() == 0


@pytest.mark.asyncio
async def test_task_awards_on_its_own_engine(user, monkeypatch):
  monkeypatch.setattr("app.tasks.achievements.DATABASE_URL", TEST_DATABASE_URL)
  await add_items(user, 10)

  await _award_for_user(user.id)

  assert await count_achievements() == 1


@pytest.mark.asyncio
async def test_create_item_triggers_check(auth_client, user, celery_delay):
  await auth_client.post("/items/", json={"title": "Buy milk"})

  celery_delay.assert_called_once_with(str(user.id))


@pytest.mark.asyncio
async def test_update_item_triggers_check(auth_client, user, celery_delay):
  created = await auth_client.post("/items/", json={"title": "Buy milk"})
  celery_delay.reset_mock()

  await auth_client.put(f"/items/{created.json()['id']}", json={"completed": True})

  celery_delay.assert_called_once_with(str(user.id))
