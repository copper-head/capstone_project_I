# Author: Duncan Truitt
# Date: 12-13-2025
#
# These routes will handle file uploads.

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from pathlib import Path
from typing import Optional
from backend.core.authentication import verify_token
from backend.db.database import pg

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    # Expect Authorization: Bearer <token>
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]

    # Verify token and get user
    with pg.get_conn() as conn:
        user = verify_token(conn, token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Save file to uploads directory
        suffix = Path(file.filename).suffix or ".bin"
        safe_name = f"user_{user['id']}_{file.filename}"
        dest_path = UPLOAD_DIR / safe_name

        content = await file.read()
        dest_path.write_bytes(content)

        # Record image metadata in DB
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO images (user_id, file_path) VALUES (%s, %s) RETURNING id",
                (user["id"], str(dest_path))
            )
            img_id = cur.fetchone()[0]
            conn.commit()

    return {"message": "Upload successful", "image_id": img_id, "path": str(dest_path)}