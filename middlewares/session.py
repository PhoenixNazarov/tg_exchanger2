from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from services.bot_query import BotQueryController


class SessionMiddleware(BaseMiddleware):
    def __init__(self, engine):
        self.engine = engine
        self.session_maker = sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            async with session.begin():
                bot_query = BotQueryController(session)

                if event.message:
                    await bot_query.get_and_update_user(event.message.from_user)
                elif event.callback_query:
                    await bot_query.get_and_update_user(event.callback_query.from_user)

                data['bot_query'] = bot_query
                result = await handler(event, data)

        await self.engine.dispose()
        return result
