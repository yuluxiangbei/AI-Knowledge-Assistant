"""安全的数据库初始化/重置脚本

用法(在项目根目录运行):
    python -m app.safe_init              # 仅建表:幂等,已有表/数据不受影响(默认,最安全)
    python -m app.safe_init --list       # 只读:打印当前数据库里实际存在的表,不改动任何东西
    python -m app.safe_init --reset      # 重置:先打印将删除的表清单,输入 y 确认后才执行

安全设计:
    1. 默认模式绝不删数据 —— create_all 只创建缺失的表
    2. --reset 必须显式传参 + 交互确认,否则取消
    3. 确认前打印将删除的表清单(来自 ORM 元数据,不写死)
    4. 连接串从 .env 读取(不硬编码账号密码)
    5. 删除/重建按外键依赖顺序自动排序(drop_all/create_all 内部处理)
"""
import argparse
import asyncio

from sqlalchemy import text

from app import models  # noqa: F401  # 导入模型,让 Base.metadata 收集到全部表
from app.db.base import Base
from app.db.session import engine


async def current_tables(conn) -> list[str]:
    """查询数据库里实际存在的表(只读)"""
    result = await conn.execute(text("SHOW TABLES"))
    return [row[0] for row in result]


async def do_init() -> None:
    """默认模式:幂等建表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] 建表完成(幂等:只创建缺失的表,已有数据不受影响)")


async def do_list() -> None:
    """只读模式:列出当前数据库中的表"""
    async with engine.connect() as conn:
        tables = await current_tables(conn)
    print(f"当前数据库共 {len(tables)} 张表:")
    for t in tables:
        print("  -", t)


async def do_reset() -> None:
    """重置模式:确认后删除全部业务表并重建"""
    app_tables = sorted(Base.metadata.tables.keys())

    async with engine.connect() as conn:
        existing = await current_tables(conn)

    print("ORM 元数据中的业务表(将删除并重建):")
    for t in app_tables:
        print("  -", t)
    orphan = [t for t in existing if t not in app_tables]
    if orphan:
        print("注意:以下库中存在但 ORM 未管理的表(不受影响,不会被删除):")
        for t in orphan:
            print("  -", t)

    answer = input("确认删除以上全部业务表并重建? 输入 y 继续,其他任意键取消: ")
    if answer.strip().lower() != "y":
        print("已取消,未做任何修改。")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] 重置完成:全部业务表已删除并重建(数据已清空)")


def main() -> None:
    parser = argparse.ArgumentParser(description="安全的数据库初始化/重置脚本")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="只读:列出当前数据库的表,不改动")
    group.add_argument("--reset", action="store_true", help="重置:删除全部业务表并重建(需输入 y 确认)")
    args = parser.parse_args()

    if args.list:
        asyncio.run(do_list())
    elif args.reset:
        asyncio.run(do_reset())
    else:
        asyncio.run(do_init())


if __name__ == "__main__":
    main()
