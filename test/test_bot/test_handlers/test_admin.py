import pytest
from aiogram.fsm.context import StorageKey

from fake_updates.private_messages import generate_message
from bot.config_reader import config

pytestmark = pytest.mark.asyncio


async def test_add_merchant(dp, bot, admin):
    await dp.feed_update(bot, generate_message('/help_admin'))
    await dp.feed_update(bot, generate_message('/add_merch 557060775'))
    await dp.feed_update(bot, generate_message('/list_merch'))

    assert 557060775 in config.merchants