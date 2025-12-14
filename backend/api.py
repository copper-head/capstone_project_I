from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from backend.db.database import DatabaseManager
from .routers import upload, main, auth


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_app() -> FastAPI:

    app = FastAPI()

    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    app.include_router(upload.router)
    app.include_router(main.router)
    app.include_router(auth.router)

    return app