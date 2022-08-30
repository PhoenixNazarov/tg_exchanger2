from __future__ import annotations
from typing import Optional, Union, Type
from sqlalchemy import select, update, or_, func

from bot.utils.misc.save_execute import *
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models.base import Base


class QueryController:
    def __init__(self, session: AsyncSession, model: Union[Type[Base], Base, None] = None):
        self._session: AsyncSession = session
        self._model: Optional[Base] = None
        self._type_model: Optional[Type[Base]] = None

        if model:
            if isinstance(model, Base):
                self._model = model
                self._type_model = type(model)
            elif issubclass(model, Base):
                self._type_model = model

    def __call__(self, model: Union[Type[Base], Base]) -> QueryController:
        return QueryController(self._session, model)

    def get_session(self):
        return self._session

    async def count_models(self):
        return await count_models(self._session, self._type_model)

    async def get_models(self):
        return await get_models(self._session, self._type_model)

    async def get_model(self, _id):
        return await get_model(self._session, self._type_model, _id)

    async def update_model_values(self, _data):
        return await update_model_values(self._session, self._model, _data)

    async def add_model(self):
        return await add_model(self._session, self._model)

    async def delete_model(self):
        return await delete_model(self._session, self._model)


async def count_models(session: AsyncSession, model: Type[Base]) -> int:
    sql = select([func.count()]).select_from(model)
    query = await session.execute(sql)
    return query.scalar()


async def get_models(session: AsyncSession, model: Type[Base]) -> list[Base]:
    sql = select(model)
    query = await session.execute(sql)
    return [u for u, in query]


async def get_model(session: AsyncSession, model: Type[Base], _id: int) -> Optional[Base]:
    sql = select(model).where(model.id == _id)
    query = await session.execute(sql)
    return query.scalar_one_or_none()


async def update_model_values(session: AsyncSession, model: Base, data: dict) -> None:
    sql = update(type(model)).where(type(model).id == model.id).values(**data)
    await session.execute(sql)
    await save_commit(session)
    for k, v in data.items():
        model.__setattr__(k, v)


async def add_model(session: AsyncSession, model: Base) -> Base:
    session.add(model)
    await save_commit(session)
    return model


async def delete_model(session: AsyncSession, model: Base) -> Base:
    await session.delete(model)
    await save_commit(session)
    return model
