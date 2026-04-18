from fastapi import APIRouter
from app.api.routes import auth, upload, share, download

api_router = APIRouter()

api_router.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
api_router.include_router(upload.router,   prefix="/upload",   tags=["Upload"])
api_router.include_router(share.router,    prefix="/share",    tags=["Share"])
api_router.include_router(download.router, prefix="/download", tags=["Download"])
