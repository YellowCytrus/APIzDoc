"""Title pages API: behavior tests — basic CRUD."""

import uuid


MINIMAL_CONTENT = {
    "elements": [],
    "paper": {"name": "a4", "width": 210.0, "height": 297.0, "margin": 20.0},
    "variables": {},
    "ignore_document_styles": True,
}


async def test_create_title_page_returns_200(client):
    unique_name = f"My Title {uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/title-pages",
        json={"name": unique_name, "content": MINIMAL_CONTENT},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == unique_name
    assert "id" in data and isinstance(data["id"], int)
    assert "content" in data
    assert data["content"]["paper"]["name"] == "a4"


async def test_list_title_pages_returns_list(client):
    name_a = f"A {uuid.uuid4().hex[:8]}"
    name_b = f"B {uuid.uuid4().hex[:8]}"
    await client.post("/title-pages", json={"name": name_a, "content": MINIMAL_CONTENT})
    await client.post("/title-pages", json={"name": name_b, "content": MINIMAL_CONTENT})
    resp = await client.get("/title-pages")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    names = [p["name"] for p in data]
    assert name_a in names and name_b in names


async def test_get_title_page_by_id_returns_200(client):
    unique_name = f"Fetch Me {uuid.uuid4().hex[:8]}"
    create = await client.post(
        "/title-pages",
        json={"name": unique_name, "content": MINIMAL_CONTENT},
    )
    tid = create.json()["id"]
    resp = await client.get(f"/title-pages/{tid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == unique_name


async def test_get_title_page_returns_404(client):
    resp = await client.get("/title-pages/99999")
    assert resp.status_code == 404


async def test_patch_title_page_returns_200(client):
    unique_name = f"Original {uuid.uuid4().hex[:8]}"
    updated_name = f"Updated {uuid.uuid4().hex[:8]}"
    create = await client.post(
        "/title-pages",
        json={"name": unique_name, "content": MINIMAL_CONTENT},
    )
    tid = create.json()["id"]
    resp = await client.patch(
        f"/title-pages/{tid}",
        json={"name": updated_name},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == updated_name


async def test_delete_title_page_returns_204(client):
    unique_name = f"To Delete {uuid.uuid4().hex[:8]}"
    create = await client.post(
        "/title-pages",
        json={"name": unique_name, "content": MINIMAL_CONTENT},
    )
    tid = create.json()["id"]
    resp = await client.delete(f"/title-pages/{tid}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/title-pages/{tid}")
    assert get_resp.status_code == 404


async def test_delete_title_page_returns_404(client):
    resp = await client.delete("/title-pages/99999")
    assert resp.status_code == 404
