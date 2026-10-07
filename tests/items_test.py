import pytest

from tests.conftest import create_user, login

@pytest.mark.asyncio
async def test_create_item(auth_client):
  response = await auth_client.post("/items/", json={"title": "Buy milk"})

  assert response.status_code == 200
  body = response.json()
  assert body["title"] == "Buy milk"
  assert body["completed"] is False
  assert "id" in body
  assert "created_at" in body


@pytest.mark.asyncio
async def test_list_items(auth_client):
  await auth_client.post("/items/", json={"title": "First", "completed": False})
  await auth_client.post("/items/", json={"title": "Second", "completed": True})

  response = await auth_client.get("/items/")

  assert response.status_code == 200
  titles = [item["title"] for item in response.json()]
  assert titles == ["First", "Second"]


@pytest.mark.asyncio
async def test_get_item(auth_client):
  created = await auth_client.post("/items/", json={"title": "Read a book", "completed": False})
  item_id = created.json()["id"]

  response = await auth_client.get(f"/items/{item_id}")

  assert response.status_code == 200
  assert response.json()["title"] == "Read a book"


@pytest.mark.asyncio
async def test_get_item_not_found(auth_client):
  response = await auth_client.get("/items/999")

  assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(auth_client):
  created = await auth_client.post("/items/", json={"title": "Old title", "completed": False})
  item_id = created.json()["id"]

  response = await auth_client.put(f"/items/{item_id}", json={"completed": True})

  assert response.status_code == 200
  body = response.json()
  assert body["completed"] is True
  assert body["title"] == "Old title"  # untouched field preserved


@pytest.mark.asyncio
async def test_update_item_not_found(auth_client):
  response = await auth_client.put("/items/999", json={"completed": True})

  assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_item(auth_client):
  created = await auth_client.post("/items/", json={"title": "Throwaway", "completed": False})
  item_id = created.json()["id"]

  response = await auth_client.delete(f"/items/{item_id}")
  assert response.status_code == 204

  follow_up = await auth_client.get(f"/items/{item_id}")
  assert follow_up.status_code == 404


@pytest.mark.asyncio
async def test_delete_item_not_found(auth_client):
  response = await auth_client.delete("/items/999")

  assert response.status_code == 404


@pytest.mark.asyncio
async def test_items_require_login(client):
  response = await client.get("/items/")

  assert response.status_code == 401


@pytest.mark.asyncio
async def test_users_cannot_see_each_others_items(auth_client):
  created = await auth_client.post("/items/", json={"title": "Alice's secret"})
  item_id = created.json()["id"]

  bob = await create_user("bob@example.com")
  await login(auth_client, bob)  # same client, now logged in as bob

  assert (await auth_client.get("/items/")).json() == []
  assert (await auth_client.get(f"/items/{item_id}")).status_code == 404
