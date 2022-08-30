import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from bot.database.models import Base


class Model(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key = True, autoincrement = True)
    data = Column(Text)


@pytest.fixture(scope = 'module')
def model():
    return Model


@pytest.fixture(scope = 'module')
def db_sess():
    from bot.services import query_controller as db_sess
    yield db_sess


@pytest_asyncio.fixture(scope="module", autouse=True)
async def mock_db_engine(db_sess, db_engine):
    engine = db_engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
