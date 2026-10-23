import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import DomainError, constraint_errors, translate
from app.models.achievement import Achievement, AchievementType
from tests.conftest import TestSession, create_user, login


def test_every_mapped_constraint_has_msg():
  errors = constraint_errors()

  assert {"uq_items_active_title", "uq_achievement_user_type"} <= errors.keys()
  assert all(e.msg for e in errors.values())


def test_error_without_field_points_at_whole_body():
  assert DomainError("oops").to_detail() == [{"loc": ["body"], "msg": "oops"}]


@pytest.mark.asyncio
async def test_duplicate_active_title_is_409(auth_client):
  await auth_client.post("/items/", json={"title": "Buy milk"})

  response = await auth_client.post("/items/", json={"title": "Buy milk"})

  assert response.status_code == 409
  detail = response.json()["detail"][0]
  assert detail["loc"] == ["body", "title"]
  assert detail["msg"] == "You already have a task with the same name"


@pytest.mark.asyncio
async def test_renaming_into_duplicate_is_409(auth_client):
  await auth_client.post("/items/", json={"title": "A"})
  b = await auth_client.post("/items/", json={"title": "B"})

  response = await auth_client.put(f"/items/{b.json()['id']}", json={"title": "A"})

  assert response.status_code == 409


@pytest.mark.asyncio
async def test_title_reusable_after_completion(auth_client):
  first = await auth_client.post("/items/", json={"title": "Run"})
  await auth_client.put(f"/items/{first.json()['id']}", json={"completed": True})

  response = await auth_client.post("/items/", json={"title": "Run"})

  assert response.status_code == 200


@pytest.mark.asyncio
async def test_same_title_allowed_for_different_users(auth_client):
  await auth_client.post("/items/", json={"title": "Shared name"})
  await login(auth_client, await create_user("bob@example.com"))

  response = await auth_client.post("/items/", json={"title": "Shared name"})

  assert response.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_achievement_translates_to_domain_error(user):
  async with TestSession() as session:
    session.add(Achievement(user_id=user.id, type=AchievementType.TEN_DONE))
    await session.commit()
    session.add(Achievement(user_id=user.id, type=AchievementType.TEN_DONE))
    with pytest.raises(IntegrityError) as exc:
      await session.commit()

  err = translate(exc.value)
  assert err is not None
  assert err.msg == "Achievement already granted"


@pytest.mark.asyncio
async def test_same_achievement_allowed_for_other_user(user):
  other = await create_user("bob@example.com")
  async with TestSession() as session:
    session.add_all([
      Achievement(user_id=user.id, type=AchievementType.TEN_DONE),
      Achievement(user_id=other.id, type=AchievementType.TEN_DONE),
    ])
    await session.commit()
