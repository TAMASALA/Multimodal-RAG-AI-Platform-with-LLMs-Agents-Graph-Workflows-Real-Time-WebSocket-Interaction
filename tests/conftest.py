"""
Shared pytest fixtures: an isolated in-memory-ish test DB and an httpx
AsyncClient wired to the FastAPI app via ASGI transport (no real network).
"""
import asyncio
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./storage/test_app.db")
os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")

from app.database.database import init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_test_db():
    await init_db()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
