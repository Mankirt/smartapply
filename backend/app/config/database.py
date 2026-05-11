import asyncpg
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

db_pool : asyncpg.Pool | None = None

async def create_pool() -> asyncpg.Pool:
    settings = get_settings()
    pool = await asyncpg.create_pool(
        dsn = settings.database_url,
        min_size = 2,
        max_size = 10
    )
    logger.info( "Database pool created successfully")

    return pool

async def close_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database pool closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    logger.info("Starting up SmartApply API...")
    db_pool = await create_pool()
    yield
    logger.info("Shutting down SmartApply API...")
    await close_pool()


async def get_db() -> asyncpg.Connection:
    async with db_pool.acquire() as connection:
        yield connection