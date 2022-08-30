import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot.config_reader import config
from fake_updates import users

Base = declarative_base()

config.test = 1


@pytest.fixture(scope = "session")
def user1():
    return 111


@pytest.fixture(scope = "session")
def user2():
    return 222


@pytest.fixture(scope = "session")
def user3():
    return users.generate_user(333)


@pytest.fixture(scope = "session")
def user1_tg():
    return users.generate_user(111)


@pytest.fixture(scope = "session")
def user2_tg():
    return users.generate_user(222)


@pytest.fixture(scope = "session")
def event_loop():
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope = "session")
async def db_engine():
    engine = create_async_engine(config.db)
    yield engine
    engine.dispose()


@pytest_asyncio.fixture(scope = 'function')
async def session(db_engine):
    """yields a SQLAlchemy connection which is rollback after the test"""
    connection = await db_engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit = False, class_ = AsyncSession)
    session = Session()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


class Model(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key = True, autoincrement = True)
    data = Column(Text)


@pytest.fixture(scope = 'session')
def model():
    return Model
