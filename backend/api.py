from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from backend.db.database import DatabaseManager
import hashlib
import secrets
from pydantic import BaseModel


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_app(db: DatabaseManager) -> FastAPI:

    @app.get("/api/get_tex_code/{tex_code_id}")
    def get_tex_code(tex_code_id: int, conn = Depends(get_db_conn)):
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, code, created_at FROM tex_codes WHERE id = %s;", (tex_code_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="TeX code not found")
        return {
            "id": row[0],
            "user_id": row[1],
            "code": row[2],
            "created_at": row[3].isoformat() if row[3] else None
        }
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


    class CreateAccountRequest(BaseModel):
        username: str
        email: str
        password: str

    @app.post("/api/auth/signup")
    def create_account(payload: CreateAccountRequest, conn = Depends(get_db_conn)):
        """Stupid simple account creation: store username, email, password_salt, password_hash."""
        # Basic validation
        if not payload.username or not payload.email or not payload.password:
            raise HTTPException(status_code=400, detail="username, email and password are required")

        # Generate salt and hash
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', payload.password.encode('utf-8'), salt.encode('utf-8'), 100_000)
        password_hash = hash_obj.hex()

        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash, password_salt)
                VALUES (%s, %s, %s, %s)
                RETURNING id, username;
                """,
                (payload.username, payload.email, password_hash, salt),
            )
            new_row = cur.fetchone()
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Simple duplicate handling (username/email unique)
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cur.close()

        return {"id": new_row[0], "username": new_row[1]}
    
    @app.post("/api/convert_document")
    async def upload_image(file: UploadFile = File(...)):
        # Check it's an image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Choose where to save it
        file_location = UPLOAD_DIR / file.filename

        # Save file to disk
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        # TO DO : Add image conversion logic
        # Return 

        return JSONResponse(
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "saved_to": str(file_location),
            }
        )

    return app