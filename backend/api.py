from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from backend.db.database import DatabaseManager


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_app(db: DatabaseManager) -> FastAPI:
    app = FastAPI()

    # Dependency that gives a connection per request
    def get_db_conn():
        conn = db.get_conn()
        try:
            yield conn
        finally:
            db.put_conn(conn)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/users")
    def list_users(conn = Depends(get_db_conn)):
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users LIMIT 10;")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "username": r[1]} for r in rows]
    
    @app.post("/upload-image")
    async def upload_image(file: UploadFile = File(...)):
        # 1. Check it's an image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # 2. Choose where to save it
        file_location = UPLOAD_DIR / file.filename

        # 3. Save file to disk
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        return JSONResponse(
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "saved_to": str(file_location),
            }
        )

    return app