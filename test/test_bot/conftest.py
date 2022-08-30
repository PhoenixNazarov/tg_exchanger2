import pytest
import pytest_asyncio

from bot.loader import bot, dp, load_db


@pytest.fixture(scope='session')
def bot():
    from bot.loader import bot
    return bot


@pytest_asyncio.fixture(scope='session')
async def dp():
    from bot.loader import dp
    await load_db()
    return dp
