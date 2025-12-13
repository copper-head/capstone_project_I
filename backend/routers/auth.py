# Author: Duncan Truitt
# Date: 12-13-2025

from fastapi import APIRouter, HTTPException, Request
from backend.core.authentication import create_user, authenticate_user
from backend.db.database import pg

# TODO: IMPLEMENT ROUTES FOR AUTHENTICATION

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")
async def register(request: Request):
    """
    Register a new user.
    
    Accepts JSON with:
    - username: str (required)
    - password: str (required)
    - email: str (optional)
    
    Returns: {"message": "User registered", "user_id": int}
    """
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        with pg.get_conn() as conn:
            user_id = create_user(conn, username, password, email)
        return {"message": "User registered successfully", "user_id": user_id}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle specific errors, e.g., unique constraint violation
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(request: Request):
    """
    Login a user.
    
    Accepts JSON with:
    - username: str
    - password: str
    
    Returns: {"message": "Login successful", "user": {...}}
    """
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        with pg.connection() as conn:
            user = authenticate_user(conn, username, password)
        if user:
            return {"message": "Login successful", "user": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout")
def logout():
    """
    Logout a user.
    
    For now, just a placeholder.
    """
    # TODO: Implement logout logic (e.g., invalidate token)
    return {"message": "Logged out"}