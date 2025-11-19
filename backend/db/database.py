import psycopg2
from psycopg2 import pool
from fastapi import FastAPI, Depends

from backend.constants import DB_CONFIG

# Create the connection pool globally (same idea)
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=DB_CONFIG['DB_USER'],
    password=DB_CONFIG['DB_PASSWORD'],
    host=DB_CONFIG['DB_HOST'],
    port=DB_CONFIG['DB_PORT'],
    database=DB_CONFIG['DB_NAME']
)

# Dependency that provides a connection per request
def get_db():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


app = FastAPI()

@app.get("/users")
def get_users(conn = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users LIMIT 5;")
    result = cur.fetchall()
    cur.close()
    return result