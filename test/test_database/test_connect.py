import pytest
from sqlalchemy import select

pytestmark = pytest.mark.asyncio


async def test_connect(session, model):
    session.add(model())
    sql = select(model).where(model.id == 1)
    query = await session.execute(sql)
    a = query.scalar_one_or_none()
    assert a.id == 1
    session.delete(a)
