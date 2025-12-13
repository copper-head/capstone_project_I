# Author: Duncan Truitt
# Date: 12-13-2025
#
# These routes will handle file uploads.

from fastapi import APIRouter

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/image")
async def upload_image():
    pass