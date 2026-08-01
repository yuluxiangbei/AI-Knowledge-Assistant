# 用 SQLAlchemy 异步引擎连接 MySQL

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession

from app.core.config import get_settings

settings = get_settings()

# 数据库连接引擎
engine = create_async_engine(
  settings.DATABASE_URL,#从配置读连接串
  echo = False, #TRUE会打印所有SQL
  pool_pre_ping = True,#用连接前先ping,防止“连接已经失效”
)
#创建会话
AsyncSessionLocal = async_sessionmaker(
  bind = engine,
  expire_on_commit= False,#commit后对象属性不失效，可以继续用
)

async def get_db() -> AsyncGenerator[AsyncSession, None]: #类型注解，表示异步生成器产出一个AsyncSession
  async with AsyncSessionLocal() as session:#进入 async with 时创建会话 → 立即 yield 交出(暂停)→ 路由用完 → 退出 async with 时关闭会话
    yield session #返回
  