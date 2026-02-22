"""Preamble API: behavior tests — GET /profiles/{id}/preamble."""

import uuid


async def test_get_preamble_returns_200_and_text(client):
    create = await client.post("/profiles", json={"name": f"Preamble {uuid.uuid4().hex[:8]}"})
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


async def test_get_preamble_includes_par_show_set_text_when_par_has_text_override(client):
    """When profile has par_style with text_override_style, preamble must contain #show par: set text(...)."""
    create = await client.post("/profiles", json={"name": f"ParOverride {uuid.uuid4().hex[:8]}"})
    pid = create.json()["id"]
    # Set par style with text override (e.g. font_size) so that show-set rule is emitted
    await client.post(
        f"/profiles/{pid}/par",
        json={
            "spacing": 1.0,
            "text_override": {"font_size": 14.0, "font": "DejaVu Sans"},
        },
    )
    resp = await client.get(f"/profiles/{pid}/preamble")
    assert resp.status_code == 200
    body = resp.text
    assert "#show par: set text(" in body
    assert "14pt" in body or "14" in body
