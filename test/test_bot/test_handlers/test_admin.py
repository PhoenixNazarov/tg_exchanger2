import pytest
from aiogram.fsm.context import StorageKey

from fake_updates.private_messages import generate_message
from bot.config_reader import config

pytestmark = pytest.mark.asyncio


async def test_add_merchant(dp, bot, admin, merchant_id, merchant):
    await dp.feed_update(bot, generate_message('/help_admin'))
    await dp.feed_update(bot, generate_message(f'/add_merch {merchant_id}'))
    await dp.feed_update(bot, generate_message('/list_merch'))

    assert merchant_id in config.merchants
