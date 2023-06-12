from fastapi import APIRouter

from app.api.v1.routes import sessions, bots

router = APIRouter()

router.include_router(bots.router, prefix="/bots", tags=["bots"])
router.include_router(sessions.router, include_in_schema=False, prefix="/sessions", tags=["sessions"])
