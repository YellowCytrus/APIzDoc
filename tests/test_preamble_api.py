"""Preamble API: behavior tests — GET /profiles/{id}/preamble."""

import uuid


async def test_get_preamble_returns_200_and_text(client):
    create = await client.post(
        "/profiles", json={"name": f"Preamble {uuid.uuid4().hex[:8]}"}
    )
    pid = create.json()["id"]
    resp = await client.get(f"/profiles/{pid}/preamble")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
    body = resp.text
    assert isinstance(body, str)
    # Preamble can be empty if profile has no styles


async def test_get_preamble_returns_404_for_nonexistent_profile(client):
    resp = await client.get("/profiles/99999/preamble")
    assert resp.status_code == 404
    assert "detail" in resp.json()
