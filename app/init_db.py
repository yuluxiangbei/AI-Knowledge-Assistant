import asyncio

from app import models
from app.db.base import Base
from app.db.session import engine

async def init():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
  asyncio.run(init())