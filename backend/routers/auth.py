# Author: Duncan Truitt
# Date: 12-13-2025

from fastapi import APIRouter

# TODO: IMPLEMENT ROUTES FOR AUTHENTICATION

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")
def register():
    pass

@router.post("/login")
def login():
    pass

@router.post("/logout")
def logout():
    pass