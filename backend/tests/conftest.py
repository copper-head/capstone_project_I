import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import os
from datetime import datetime

# Ensure project root is on sys.path so 'backend' package imports work
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Disable real DB pool initialization for tests
os.environ.setdefault("DISABLE_DB_INIT", "1")

from backend.db import database as db_module
from backend.core import authentication as auth_module
from backend.api import create_app
import backend.routers.tex as tex_router
import backend.routers.upload as upload_router


class FakeCursor:
    def __init__(self, rows=None):
        # Base rows represent the "table" results a real DB could return.
        self._base_rows = list(rows or [])
        self._rows = list(self._base_rows)

    def execute(self, query, params=None):
        self._last_query = (query, params)
        self._rows = self._apply_query(query, params)

    def _apply_query(self, query, params):
        # Very small SQL-ish interpreter for the repo's test queries.
        # This keeps tests meaningful without needing a real Postgres.
        if not query:
            return list(self._base_rows)

        q = " ".join(str(query).split()).lower()
        p = params or ()
        rows = list(self._base_rows)

        # /tex/images-to-latex: SELECT id, file_path ... WHERE id = ANY(%s) AND user_id = %s ORDER BY id
        if "where id = any" in q and p:
            wanted = set(p[0] or [])
            rows = [r for r in rows if r and r[0] in wanted]
            rows.sort(key=lambda r: r[0])
            return rows

        # /tex/images: list images, optional batch filter, plus LIMIT/OFFSET and ORDER BY uploaded_at DESC, id DESC
        if "from images" in q and "where user_id" in q and p:
            batch_id = None
            limit = None
            offset = 0

            if "batch_id = %s" in q:
                # (user_id, batch_id, limit, offset)
                if len(p) >= 4:
                    batch_id = p[1]
                    limit = p[2]
                    offset = p[3]
            else:
                # (user_id, limit, offset)
                if len(p) >= 3:
                    limit = p[1]
                    offset = p[2]

            if batch_id is not None:
                rows = [r for r in rows if len(r) >= 4 and r[3] == batch_id]

            # Apply ordering if tuples look like (id, file_path, uploaded_at, batch_id)
            if rows and len(rows[0]) >= 3:
                def _key(r):
                    uploaded_at = r[2]
                    if uploaded_at is None:
                        uploaded_at = datetime.min
                    return (uploaded_at, r[0])
                rows.sort(key=_key, reverse=True)

            try:
                offset_i = int(offset or 0)
            except (TypeError, ValueError):
                offset_i = 0
            if offset_i < 0:
                offset_i = 0

            if limit is None:
                return rows[offset_i:]

            try:
                limit_i = int(limit)
            except (TypeError, ValueError):
                limit_i = len(rows)
            if limit_i < 0:
                limit_i = 0
            return rows[offset_i: offset_i + limit_i]

        return list(self._base_rows)

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConn:
    def __init__(self, rows=None):
        self._rows = rows or []

    def cursor(self):
        return FakeCursor(self._rows)


class FakePG:
    def __init__(self):
        # Default rows can be overridden per-test via monkeypatching
        self._rows = []

    def get_conn(self):
        return FakeConn(self._rows)

    def put_conn(self, conn):
        pass


@pytest.fixture()
def fake_pg():
    return FakePG()


@pytest.fixture()
def fake_verify_token():
    def _verify(_conn, token):
        if token == "valid":
            return {"id": 1, "username": "tester"}
        return None
    return _verify


@pytest.fixture()
def client(monkeypatch, fake_pg, fake_verify_token):
    # Apply monkeypatches BEFORE app creation so routers get patched deps
    monkeypatch.setattr(db_module, "pg", fake_pg)
    # Patch router-local references to pg and verify_token as they were imported directly
    monkeypatch.setattr(tex_router, "pg", fake_pg)
    monkeypatch.setattr(upload_router, "pg", fake_pg)
    monkeypatch.setattr(tex_router, "verify_token", fake_verify_token)
    monkeypatch.setattr(upload_router, "verify_token", fake_verify_token)
    app = create_app()
    return TestClient(app)
