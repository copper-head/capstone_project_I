import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import os

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
        self._rows = rows or []

    def execute(self, query, params=None):
        self._last_query = (query, params)

    def fetchall(self):
        return self._rows

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
