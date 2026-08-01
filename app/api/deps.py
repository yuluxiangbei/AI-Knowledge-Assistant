"""API 依赖:提供数据库会话"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
# DbDep:FastAPI 依赖别名——路由里写 db: DbDep 就能拿到数据库会话
DbDep = Annotated[AsyncSession,Depends(get_db)] #类型是 AsyncSession,通过get_db来获取

