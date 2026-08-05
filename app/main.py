from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import api_router
from app.core.config import get_settings
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,#允许带凭证
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def get_health():
  return {"status":"ok"}

