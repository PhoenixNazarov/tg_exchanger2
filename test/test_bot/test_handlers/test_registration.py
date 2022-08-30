import pytest

from fake_updates.private_messages import generate_message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from aiogram.fsm.context import StorageKey

pytestmark = pytest.mark.asyncio


async def test_start_message(dp, bot):
    state = await dp.storage.get_state(bot, 123)
    await dp.feed_update(bot, generate_message('/start'))
    await dp.storage.get_state(bot, StorageKey(bot.id, chat_id = 123, user_id = 123))
