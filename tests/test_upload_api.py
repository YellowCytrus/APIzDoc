"""Upload image API: POST /upload-image, GET /images/{filename}."""

# Минимальный валидный PNG (1x1 пиксель)
MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


async def test_upload_image_returns_200_and_path(client):
    """POST /upload-image возвращает path для вставки в Markdown."""
    files = {"file": ("test.png", MINIMAL_PNG, "image/png")}
    resp = await client.post("/upload-image", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "path" in data
    assert data["path"].startswith("images/")
    assert data["path"].endswith(".png")


async def test_upload_image_and_serve_via_static(client):
    """Загруженное изображение доступно по GET /images/{filename}."""
    files = {"file": ("serve_test.png", MINIMAL_PNG, "image/png")}
    up = await client.post("/upload-image", files=files)
    assert up.status_code == 200
    path = up.json()["path"]
    filename = path.replace("images/", "")
    get_resp = await client.get(f"/images/{filename}")
    assert get_resp.status_code == 200
    assert get_resp.content == MINIMAL_PNG


async def test_upload_image_rejects_missing_filename(client):
    """Пустое имя файла — FastAPI возвращает 422 (validation) или наш 400."""
    files = {"file": ("", MINIMAL_PNG, "image/png")}
    resp = await client.post("/upload-image", files=files)
    assert resp.status_code in (400, 422)


async def test_upload_image_400_unsupported_extension(client):
    files = {"file": ("x.exe", b"fake", "application/octet-stream")}
    resp = await client.post("/upload-image", files=files)
    assert resp.status_code == 400


async def test_upload_image_400_unsupported_content_type(client):
    files = {"file": ("x.png", MINIMAL_PNG, "application/pdf")}
    resp = await client.post("/upload-image", files=files)
    assert resp.status_code == 400


async def test_upload_image_413_too_large(client):
    big = b"\x89PNG" + b"\x00" * (5 * 1024 * 1024 + 1)
    files = {"file": ("big.png", big, "image/png")}
    resp = await client.post("/upload-image", files=files)
    assert resp.status_code == 413
