import names
import pytest

from bot.services import users
from fake_updates.users import change_user

pytestmark = pytest.mark.asyncio


async def test_get_empty(user1, session_controller):
    assert not await users.get_user(session_controller, user1)


async def test_not_equals(user1, user2, session_controller):
    user = await users.create_user(session_controller,
                                   user_id = user1,
                                   first_name = '123',
                                   last_name = '123',
                                   username = '123',
                                   language = '123',
                                   )
    user3 = await users.create_user(session_controller,
                                    user_id = user2,
                                    first_name = '123',
                                    last_name = '321',
                                    username = '321',
                                    language = '312',
                                    )
    assert user != user3
    assert user == await users.get_user(session_controller, user1)


async def test_add(user1, session_controller):
    user = await users.create_user(session_controller,
                                   user_id = user1,
                                   first_name = '123',
                                   last_name = '123',
                                   username = '123',
                                   language = '123',
                                   )
    assert user.id == user1
    assert user.first_name == '123'
    assert user.last_name == '123'
    assert user.username == '123'
    assert user.language == '123'

    user2 = await users.get_user(session_controller, user1)

    assert user == user2


async def test_update(user1, session_controller):
    user = await users.create_user(session_controller,
                                   user_id = user1,
                                   first_name = '123',
                                   last_name = '123',
                                   username = '123',
                                   language = '123',
                                   )

    new_user = await users.update_user(session_controller, user, {
        'first_name': '1412412'
    })
    user2 = await users.get_user(session_controller, user1)

    assert user == user2 == new_user
    assert user.id == user1
    assert user.first_name == '1412412'
    assert user.last_name == '123'
    assert user.username == '123'
    assert user.language == '123'
