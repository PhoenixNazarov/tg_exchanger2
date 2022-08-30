from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.bot_query import BotQueryController
from bot.services.query_controller import QueryController


class SessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        session: AsyncSession = self.session_maker()
        bot_query = BotQueryController(QueryController(session))

        if event.message:
            await bot_query.get_and_update_user(event.message.from_user)
        elif event.callback_query:
            await bot_query.get_and_update_user(event.callback_query.from_user)

        data['bot_query'] = bot_query
        result = await handler(event, data)

        await session.close()
        return result
