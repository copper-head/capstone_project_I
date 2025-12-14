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


@router.post("/batch")
async def upload_batch(
    files: list[UploadFile] = File(...),
    authorization: Optional[str] = Header(None),
    batch_name: Optional[str] = None,
):
    # Expect Authorization: Bearer <token>
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    with pg.get_conn() as conn:
        user = verify_token(conn, token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Optional: create a batch record
        batch_id = None
        if batch_name:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO image_batches (user_id, batch_name) VALUES (%s, %s) RETURNING id",
                    (user["id"], batch_name)
                )
                batch_id = cur.fetchone()[0]
                conn.commit()

        saved = []
        for f in files:
            safe_name = f"user_{user['id']}_{f.filename}"
            dest_path = UPLOAD_DIR / safe_name
            content = await f.read()
            dest_path.write_bytes(content)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO images (user_id, file_path, batch_id) VALUES (%s, %s, %s) RETURNING id",
                    (user["id"], str(dest_path), batch_id)
                )
                img_id = cur.fetchone()[0]
                conn.commit()
            saved.append({"image_id": img_id, "path": str(dest_path)})

    return {"message": "Batch upload successful", "batch_id": batch_id, "items": saved}