import pytest

@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post("/items/", json={"title": "Buy milk"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["completed"] is False
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_list_items(client):
    await client.post("/items/", json={"title": "First", "completed": False})
    await client.post("/items/", json={"title": "Second", "completed": True})

    response = await client.get("/items/")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["First", "Second"]


@pytest.mark.asyncio
async def test_get_item(client):
    created = await client.post("/items/", json={"title": "Read a book", "completed": False})
    item_id = created.json()["id"]

    response = await client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Read a book"


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    response = await client.get("/items/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(client):
    created = await client.post("/items/", json={"title": "Old title", "completed": False})
    item_id = created.json()["id"]

    response = await client.put(f"/items/{item_id}", json={"completed": True})

    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["title"] == "Old title"  # untouched field preserved


@pytest.mark.asyncio
async def test_update_item_not_found(client):
    response = await client.put("/items/999", json={"completed": True})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_item(client):
    created = await client.post("/items/", json={"title": "Throwaway", "completed": False})
    item_id = created.json()["id"]

    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 200

    follow_up = await client.get(f"/items/{item_id}")
    assert follow_up.status_code == 404


@pytest.mark.asyncio
async def test_delete_item_not_found(client):
    response = await client.delete("/items/999")

    assert response.status_code == 404
