from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from config_reader import config
from database.models import Base


async def create_db_session():
    engine = create_async_engine(config.db, future = True,
                                 connect_args = {"server_settings": {"jit": "off"}})

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit = False, class_ = AsyncSession
    )

    return engine
