import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models import Base

# 测试数据库URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/login_demo_test"

# 创建测试引擎
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

AsyncTestSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """设置测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator:
    """创建测试数据库会话"""
    async with AsyncTestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app)
    ) as ac:
        yield ac
