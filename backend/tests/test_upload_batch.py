# I AM ONLY KEEPING THIS FOR INCREASED COVERAGE
# This route is not being used by the frontend currently.
# but for sake of coverage, we keep tests here.

import io


def test_upload_batch_requires_auth(client):
    files = [("files", ("a.png", b"A", "image/png"))]
    r = client.post("/upload/batch", files=files)
    assert r.status_code == 401


def test_upload_batch_empty_files(client, fake_verify_token):
    # Missing required 'files' field leads to 422 from validation
    r = client.post("/upload/batch", headers={"Authorization": "Bearer valid"})
    assert r.status_code == 422


def test_upload_batch_happy_path(client, fake_pg, fake_verify_token, monkeypatch):
    # Mock file writes
    from pathlib import Path
    writes = {}
    def fake_write_bytes(self, data):
        writes[str(self)] = data
        return len(data)
    monkeypatch.setattr(Path, "write_bytes", fake_write_bytes)

    # Mock DB cursors: first optional batch insert, then image inserts
    class BatchCursor:
        def __init__(self, rows):
            self._rows = rows
            self._commit_called = False
        def execute(self, q, p=None):
            self._last = (q, p)
        def fetchone(self):
            return self._rows.pop(0) if self._rows else (100,)  # default batch id
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
    class BatchConn:
        def __init__(self):
            # First fetchone for batch_id, subsequent for image ids
            self._rows = [(77,), (5,), (6,)]
        def cursor(self):
            return BatchCursor(self._rows)
        def commit(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
    fake_pg.get_conn = lambda: BatchConn()

    files = [
        ("files", ("x.png", io.BytesIO(b"X"), "image/png")),
        ("files", ("y.png", io.BytesIO(b"Y"), "image/png")),
    ]

    r = client.post(
        "/upload/batch?batch_name=myset",
        headers={"Authorization": "Bearer valid"},
        files=files,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["batch_id"] == 77
    assert len(data["items"]) == 2
    assert {item["image_id"] for item in data["items"]} == {5, 6}
    # Confirm writes occurred
    assert any(path.endswith("x.png") for path in writes)
    assert any(path.endswith("y.png") for path in writes)
