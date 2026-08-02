from fastapi import APIRouter

from app.api.routers import auth,users,conversations

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(conversations.router)
