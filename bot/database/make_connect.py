from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base
from bot.config_reader import config


async def create_db_session():
    db_url = config.db
    if config.test:
        db_url = config.db_test

    engine = create_async_engine(db_url, future = True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit = False, class_ = AsyncSession
    )

    return async_session
