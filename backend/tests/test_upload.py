import io


def test_upload_image_requires_auth(client):
    r = client.post("/upload/image", files={"file": ("note.png", b"123", "image/png")})
    assert r.status_code == 401


def test_upload_image_happy_path(client, fake_pg, fake_verify_token, monkeypatch):
    # Mock filesystem writes
    from pathlib import Path

    written = {}

    def fake_write_bytes(self, data: bytes):
        written[str(self)] = data
        return len(data)

    monkeypatch.setattr(Path, "write_bytes", fake_write_bytes)

    # Mock DB insert returning id
    class InsertCursor:
        def __init__(self):
            self._rows = [(42,)]
            self._committed = False

        def execute(self, query, params=None):
            self._last_query = (query, params)

        def fetchone(self):
            return self._rows[0]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class InsertConn:
        def cursor(self):
            return InsertCursor()
        def commit(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    fake_pg._rows = []
    fake_pg.get_conn = lambda: InsertConn()

    f = io.BytesIO(b"PNGDATA")
    r = client.post(
        "/upload/image",
        headers={"Authorization": "Bearer valid"},
        files={"file": ("note.png", f, "image/png")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["image_id"] == 42
    # Ensure file was "written"
    assert any(path.endswith("note.png") for path in written.keys())
