import pytest

from fake_updates.private_messages import generate_message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message

from bot.services.bot_query import BotQueryController

pytestmark = pytest.mark.asyncio


async def test_session_middleware_message(local_dp, local_bot):
    @local_dp.message()
    async def handler(message: Message, bot_query):
        assert message.text == 'start'
        assert isinstance(bot_query, BotQueryController)

    await local_dp.feed_update(local_bot, generate_message('start'))
