import pytest
import pytest_asyncio

from fake_updates.private_messages import generate_message, generate_contact


@pytest.fixture(scope = 'session')
def new_user_message():
    pass


@pytest.fixture(scope = 'session')
def merchant_id():
    return 5430605919


@pytest_asyncio.fixture(scope = 'session')
async def merchant(dp, bot, merchant_id):
    await dp.feed_update(bot, generate_message('/start', user_id = merchant_id))
    await dp.feed_update(bot, generate_contact('7908218', user_id = merchant_id))


@pytest_asyncio.fixture(scope = 'session')
async def admin(dp, bot):
    await dp.feed_update(bot, generate_message('/start'))
    await dp.feed_update(bot, generate_contact('123123123'))


@pytest_asyncio.fixture(scope = 'session')
async def setup_user_merchant_trans(dp, bot, admin, merchant_id, merchant):
    await dp.feed_update(bot, generate_message('/help_admin'))
    try:
        await dp.feed_update(bot, generate_message(f'/add_merch {merchant_id}'))
    except:
        pass
    await dp.feed_update(bot, generate_message('/list_merch'))
