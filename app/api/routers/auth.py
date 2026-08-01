"""认证路由:注册 / 登录"""
from fastapi import APIRouter,HTTPException, status
from sqlalchemy import select

from app.api.deps import DbDep
from app.core.security import create_access_token,hash_password,verify_password
from app.models import User
from app.schemas.auth import LoginRequest,RegisterRequest,TokenOut,UserOut

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db : DbDep):
  existing = await db.scalar(select(User).where(User.username == payload.username))
  if existing:
    raise HTTPException(status_code=409,detail="用户名已存在")

  user = User(username = payload.username, hashed_password = hash_password(payload.password))

  db.add(user)
  await db.commit()
  await db.refresh(user)

  return TokenOut(access_token=create_access_token(user.id),user = UserOut.model_validate(user))


@router.post("/login",response_model=TokenOut)
async def login(payload: LoginRequest, db: DbDep):
  user = await db.scalar(select(User).where(User.username == payload.username))
  if not user or not verify_password(payload.password,user.hashed_password):
    raise HTTPException(status_code=401,detail="用户名或密码错误")

  return TokenOut(access_token=create_access_token(user.id),user = UserOut.model_validate(user))
  
