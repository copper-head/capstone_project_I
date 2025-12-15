import time
import os
import psycopg2
from psycopg2 import pool
from backend.constants import DB_CONFIG


class DatabaseManager:
    def __init__(self):
        self._pool = None
        self._init_pool_with_retry()

    def _init_pool_with_retry(self, retries: int = 30, delay: float = 1.0):
        last_err = None
        for _ in range(retries):
            try:
                self._pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    user=DB_CONFIG["DB_USER"],
                    password=DB_CONFIG["DB_PASSWORD"],
                    host=DB_CONFIG["DB_HOST"],
                    port=DB_CONFIG["DB_PORT"],
                    database=DB_CONFIG["DB_NAME"],
                )
                return
            except Exception as e:
                last_err = e
                time.sleep(delay)
        raise last_err

    def get_conn(self):
        return self._pool.getconn()

    def put_conn(self, conn):
        self._pool.putconn(conn)

    def close_all(self):
        self._pool.closeall()
    
"""
Initialize a global database manager instance.
In test environments, set environment variable DISABLE_DB_INIT=1 to skip
initializing a real connection pool (tests will monkeypatch 'pg').
"""
if os.environ.get("DISABLE_DB_INIT") == "1":
    pg = None
else:
    pg = DatabaseManager()