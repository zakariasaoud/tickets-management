from fastapi import FastAPI

from app.db.sqlite import close_sqlite_connection, create_sqlite_connection, database
from app.models.models import Base
from app.routers import tickets_api

app = FastAPI(
    title="Tickets management API",
    description="A FastAPI app to manage tickets using SQLite database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def on_startup():
    await create_sqlite_connection()
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def on_shutdown():
    await close_sqlite_connection()


app.include_router(tickets_api.router, prefix="/tickets", tags=["Tickets"])
