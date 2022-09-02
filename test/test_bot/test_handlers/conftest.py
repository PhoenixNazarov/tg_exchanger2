import pytest
import pytest_asyncio

from bot.database import User
from bot.utils.misc.save_execute import save_commit
from fake_updates.private_messages import generate_message, generate_contact




@pytest.fixture(scope='session')
def new_user_message():
    pass


@pytest.fixture(scope='session')
def merchant():
    pass


@pytest_asyncio.fixture(scope='session')
async def admin(dp, bot):
    await dp.feed_update(bot, generate_message('/start'))
    await dp.feed_update(bot, generate_contact('123123123'))
