from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.meetings import router as meetings_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(meetings_router)
