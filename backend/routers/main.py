# Author: Duncan Truitt
# Date: 12-13-2025
#
# This file just defines some basic routes for the api.

from fastapi import APIRouter

router = APIRouter(
    prefix="/",
    tags=["main"]
)

@router.get("/")
def root():
    return {"message": "API is running"}

@router.get("/health")
def health_check():
    return {"status": "ok"}
