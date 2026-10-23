import pytest

from tests.conftest import create_user, login

@pytest.mark.asyncio
async def test_create_item(auth_client):
  response = await auth_client.post("/items/", json={"title": "Buy milk"})

  assert response.status_code == 200
  body = response.json()
  assert body["title"] == "Buy milk"
  assert body["completed_at"] is None
  assert "id" in body
  assert "created_at" in body


@pytest.mark.asyncio
async def test_list_items(auth_client):
  first = await auth_client.post("/items/", json={"title": "First"})
  await auth_client.post("/items/", json={"title": "Second"})
  await auth_client.put(f"/items/{first.json()['id']}", json={"completed": True})

  response = await auth_client.get("/items/")

  assert response.status_code == 200
  titles = [item["title"] for item in response.json()]
  assert titles == ["Second", "First"]  # unfinished first, even though First was updated last


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
  assert body["completed_at"] is not None
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


@pytest.mark.asyncio
async def test_start_item_sets_started_at(auth_client):
  created = await auth_client.post("/items/", json={"title": "Begin me"})

  response = await auth_client.put(f"/items/{created.json()['id']}", json={"started": True})

  assert response.status_code == 200
  assert response.json()["started_at"] is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [{}, {"title": ""}, {"title": "   "}, {"title": 123}])
async def test_create_item_invalid_body(auth_client, body):
  response = await auth_client.post("/items/", json=body)

  assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_item_blank_title(auth_client):
  created = await auth_client.post("/items/", json={"title": "Fine"})

  response = await auth_client.put(f"/items/{created.json()['id']}", json={"title": " "})

  assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["get", "put", "delete"])
async def test_item_id_must_be_int(auth_client, method):
  response = await getattr(auth_client, method)("/items/abc")

  assert response.status_code == 422


@pytest.mark.asyncio
async def test_random_item(auth_client):
  created = await auth_client.post("/items/", json={"title": "Only one"})

  response = await auth_client.get("/items/random")

  assert response.status_code == 200
  assert response.json() == {"id": created.json()["id"]}


@pytest.mark.asyncio
async def test_random_item_none_unfinished(auth_client):
  assert (await auth_client.get("/items/random")).status_code == 404

  created = await auth_client.post("/items/", json={"title": "Done soon"})
  await auth_client.put(f"/items/{created.json()['id']}", json={"completed": True})

  assert (await auth_client.get("/items/random")).status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("method,url", [
  ("post", "/items/"), ("get", "/items/random"), ("get", "/items/1"),
  ("put", "/items/1"), ("delete", "/items/1"),
])
async def test_every_item_endpoint_requires_login(client, method, url):
  response = await getattr(client, method)(url)

  assert response.status_code == 401
