from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, func
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base, Merchant
from bot.config_reader import config


async def create_db_session():
    db_url = config.db
    if config.test:
        db_url = config.db_test

    engine = create_async_engine(db_url, future = True)

    async with engine.begin() as conn:
        if config.test:
            await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit = False, class_ = AsyncSession
    )

    async with async_session() as session:
        merchants = (await session.execute(select(Merchant))).all()
        merchants = [u for u, in merchants]
        for i in merchants:
            config.merchants.append(i.id)

    return async_session
