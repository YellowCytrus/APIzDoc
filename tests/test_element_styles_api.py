"""Element styles API: bullet_list as representative — behavior tests."""

import uuid


async def test_post_bullet_list_creates_styles(client):
    create = await client.post("/profiles", json={"name": f"P {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    resp = await client.post(
        f"/profiles/{pid}/bullet_list",
        json={"tight": False, "marker": ["*"], "spacing": "loose"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tight"] is False
    assert data["marker"] == ["*", "- ", "‣"]  # padded to 3 from default
    assert data["spacing"] == "loose"


async def test_get_bullet_list_returns_styles(client):
    create = await client.post("/profiles", json={"name": f"P2 {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    await client.post(f"/profiles/{pid}/bullet_list", json={"tight": True})
    resp = await client.get(f"/profiles/{pid}/bullet_list")
    assert resp.status_code == 200
    assert resp.json()["tight"] is True


async def test_get_bullet_list_creates_defaults_if_missing(client):
    create = await client.post("/profiles", json={"name": f"P3 {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    resp = await client.get(f"/profiles/{pid}/bullet_list")
    assert resp.status_code == 200
    data = resp.json()
    assert "tight" in data
    assert "marker" in data


async def test_patch_bullet_list_returns_404_when_not_set(client):
    create = await client.post("/profiles", json={"name": f"P4 {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    resp = await client.patch(f"/profiles/{pid}/bullet_list", json={"tight": False})
    assert resp.status_code == 404


async def test_patch_bullet_list_returns_200_after_post(client):
    create = await client.post("/profiles", json={"name": f"P5 {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    await client.post(f"/profiles/{pid}/bullet_list", json={})
    resp = await client.patch(f"/profiles/{pid}/bullet_list", json={"tight": False})
    assert resp.status_code == 200
    assert resp.json()["tight"] is False


async def test_element_styles_404_for_nonexistent_profile(client):
    resp = await client.get("/profiles/99999/bullet_list")
    assert resp.status_code == 404
    resp = await client.post("/profiles/99999/bullet_list", json={})
    assert resp.status_code == 404
    resp = await client.patch("/profiles/99999/bullet_list", json={"tight": True})
    assert resp.status_code == 404
