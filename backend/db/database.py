import psycopg2
from psycopg2 import pool
from backend.constants import DB_CONFIG


class DatabaseManager:
    def __init__(self):
        self._pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=DB_CONFIG["DB_USER"],
            password=DB_CONFIG["DB_PASSWORD"],
            host=DB_CONFIG["DB_HOST"],
            port=DB_CONFIG["DB_PORT"],
            database=DB_CONFIG["DB_NAME"],
        )

    def get_conn(self):
        return self._pool.getconn()

    def put_conn(self, conn):
        self._pool.putconn(conn)

    def close_all(self):
        self._pool.closeall()