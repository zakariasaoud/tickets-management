from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config.settings import SQLITE_DATABASE_URL
import asyncio


class SqliteDatabase:
    engine: AsyncEngine = None
    async_session: sessionmaker = None


database = SqliteDatabase()


async def create_sqlite_connection(retries=10, delay=2):
    for attempt in range(retries):
        try:
            database.engine = create_async_engine(SQLITE_DATABASE_URL, future=True)
            database.async_session = sessionmaker(
                database.engine, expire_on_commit=False, class_=AsyncSession
            )
            # Test the connection with the SQLITE database
            async with database.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("The SQLITE connection is created")
            return
        except Exception as e:
            print(f"Cannot connect to SQLITE database, because of {e}")
            await asyncio.sleep(delay)


# Closing the SQLITE connection
async def close_sqlite_connection():
    if database.engine:
        try:
            await database.engine.dispose()
            print("The SQLITE connection is closed")
        except Exception as e:
            print(f"Cannot close the SQLITE connection because of {e}")


# This function will be used as Dependency for our FastAPI routers
async def get_db() -> AsyncSession:
    if not database.async_session:
        raise RuntimeError("SQLITE database is not connected")
    async with database.async_session() as session:
        yield session
