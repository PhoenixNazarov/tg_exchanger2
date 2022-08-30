import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from bot.database.models import Base
from bot.config_reader import config


async def create_db_session():

    engine = create_async_engine(config.db,
                                 future = True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_db_session())
