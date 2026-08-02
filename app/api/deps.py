"""API 依赖:提供数据库会话"""
from typing import Annotated

from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User
# DbDep:FastAPI 依赖别名——路由里写 db: DbDep 就能拿到数据库会话
DbDep = Annotated[AsyncSession,Depends(get_db)] #类型是 AsyncSession,通过get_db来获取

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: Annotated[str,Depends(oauth2_scheme)], db:DbDep) -> User:
  credentials_exception = HTTPException(status_code=401,detail="...",headers={"WWW-Authenticate":"Bearer"})
  try:
    payload = decode_access_token(token)
    user_id = int(payload["sub"])

  except Exception:
    raise credentials_exception
  user = await db.get(User,user_id)
  if not user:
    raise credentials_exception
  return user

# ④ 收尾定义别名
CurrentUser = Annotated[User, Depends(get_current_user)]

  


