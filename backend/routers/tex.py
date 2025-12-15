from fastapi import APIRouter, HTTPException, Header
from fastapi import Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from backend.core.authentication import verify_token
from backend.db.database import pg
from backend.core.agent import generate_latex_from_images

router = APIRouter(
    prefix="/tex",
    tags=["tex"]
)

class ImagesToLatexRequest(BaseModel):
    image_ids: List[int]


@router.post("/images-to-latex")
async def images_to_latex(
    payload: ImagesToLatexRequest,
    authorization: Optional[str] = Header(None),
):
    # Require Bearer token
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]

    if not payload.image_ids:
        raise HTTPException(status_code=400, detail="No image IDs provided")

    conn = pg.get_conn()
    try:
        user = verify_token(conn, token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Fetch paths for provided image IDs that belong to the user
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, file_path FROM images
                WHERE id = ANY(%s) AND user_id = %s
                ORDER BY id
                """,
                (payload.image_ids, user["id"]),
            )
            rows = cur.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No matching images found for user")

        # Check for missing IDs
        found_ids = {row[0] for row in rows}
        missing = [i for i in payload.image_ids if i not in found_ids]
        if missing:
            # Not fatal; return LaTeX for those found and warn
            warning = f"Some image IDs not found or not owned: {missing}"
        else:
            warning = None

        paths = [row[1] for row in rows]
        latex = generate_latex_from_images(paths)

        # Return as a downloadable .tex file
        filename = "images_includes.tex"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        return StreamingResponse(
            iter([latex.encode("utf-8")]),
            media_type="application/x-tex",
            headers=headers,
        )
    finally:
        pg.put_conn(conn)


@router.get("/images")
async def list_user_images(
    authorization: Optional[str] = Header(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    batch_id: Optional[int] = None,
):
    # Require Bearer token
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]

    conn = pg.get_conn()
    try:
        user = verify_token(conn, token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        with conn.cursor() as cur:
            if batch_id is not None:
                cur.execute(
                    """
                    SELECT id, file_path, uploaded_at, batch_id
                    FROM images
                    WHERE user_id = %s AND batch_id = %s
                    ORDER BY uploaded_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user["id"], batch_id, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT id, file_path, uploaded_at, batch_id
                    FROM images
                    WHERE user_id = %s
                    ORDER BY uploaded_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user["id"], limit, offset),
                )
            rows = cur.fetchall()

        images = [
            {
                "id": r[0],
                "file_path": r[1],
                "uploaded_at": r[2].isoformat() if r[2] else None,
                "batch_id": r[3],
            }
            for r in rows
        ]

        return {"count": len(images), "images": images, "limit": limit, "offset": offset, "batch_id": batch_id}
    finally:
        pg.put_conn(conn)
