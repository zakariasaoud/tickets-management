import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.models.models import Base
from app.db.sqlite import create_sqlite_connection, database


@pytest.fixture
def ticket_id() -> str:
    return "e8a69b44-98dc-4fc1-9f24-b764fd8c89a2"


@pytest.fixture(scope="session", autouse=True)
def setup_database_sync():
    asyncio.run(setup_database())


async def setup_database():
    await create_sqlite_connection()
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
