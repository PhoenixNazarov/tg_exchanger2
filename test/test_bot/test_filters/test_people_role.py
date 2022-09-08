import datetime

import pytest
from aiogram.types import Message, User

from bot.filters.people_role import PeopleRoleFilter, PeopleRoles

pytestmark = pytest.mark.asyncio

#
# @pytest.fixture
# def unregister_message():
#     return Message(
#         message_id = 42,
#         date = datetime.datetime.now(),
#         text = "/test",
#         chat = 1,
#         from_user = User(id = 1, is_bot = False, first_name = "Test")
#     )
#
#
# @pytest.fixture
# def user_message():
#     return Message(
#         message_id = 42,
#         date = datetime.datetime.now(),
#         text = "/test",
#         chat = 1,
#         from_user = User(id = 1, is_bot = False, first_name = "Test")
#     )
#
#
# @pytest.fixture
# def merchant_message():
#     return Message(
#         message_id = 42,
#         date = datetime.datetime.now(),
#         text = "/test",
#         chat = 1,
#         from_user = User(id = 1, is_bot = False, first_name = "Test")
#     )
#
#
# @pytest.fixture
# def admin_message():
#     return Message(
#         message_id = 42,
#         date = datetime.datetime.now(),
#         text = "/test",
#         chat = 1,
#         from_user = User(id = 1, is_bot = False, first_name = "Test")
#     )
#
#
# async def test_init():
#     filter1 = PeopleRoleFilter(people_role = PeopleRoles.UNREGISTER)
#     filter2 = PeopleRoleFilter(people_role = [PeopleRoles.USER, PeopleRoles.ADMIN])
#
#     await filter1(None)
#     await filter2(None)
#     await PeopleRoles.UNREGISTER == filter1.people_role
#     await [PeopleRoles.USER, PeopleRoles.ADMIN] == filter2.people_role
#
#
# async def test_is(unregister_message, user_message, merchant_message, admin_message):
#     _filter = PeopleRoleFilter(people_role = PeopleRoles.UNREGISTER)
#     assert await _filter(unregister_message) == True
#     assert await _filter(user_message) == False
#     assert await _filter(merchant_message) == False
#     assert await _filter(admin_message) == False
#
#     _filter = PeopleRoleFilter(people_role = PeopleRoles.USER)
#     assert await _filter(unregister_message) == False
#     assert await _filter(user_message) == True
#     assert await _filter(merchant_message) == True
#     assert await _filter(admin_message) == True
#
#     _filter = PeopleRoleFilter(people_role = PeopleRoles.MERCHANT)
#     assert await _filter(unregister_message) == False
#     assert await _filter(user_message) == False
#     assert await _filter(merchant_message) == True
#     assert await _filter(admin_message) == True
#
#     _filter = PeopleRoleFilter(people_role = PeopleRoles.ADMIN)
#     assert await _filter(unregister_message) == False
#     assert await _filter(user_message) == False
#     assert await _filter(merchant_message) == False
#     assert await _filter(admin_message) == True
#
#
# async def test_in(unregister_message, user_message, merchant_message, admin_message):
#     _filter = PeopleRoleFilter(people_role = [PeopleRoles.UNREGISTER, PeopleRoles.USER])
#     assert await _filter(unregister_message) == True
#     assert await _filter(user_message) == True
#     assert await _filter(merchant_message) == True
#     assert await _filter(admin_message) == True
#
#     _filter = PeopleRoleFilter(people_role = [PeopleRoles.USER, PeopleRoles.ADMIN])
#     assert await _filter(unregister_message) == False
#     assert await _filter(user_message) == True
#     assert await _filter(merchant_message) == False
#     assert await _filter(admin_message) == True
#
#     _filter = PeopleRoleFilter(people_role = [PeopleRoles.MERCHANT, PeopleRoles.ADMIN])
#     assert await _filter(unregister_message) == False
#     assert await _filter(user_message) == False
#     assert await _filter(merchant_message) == True
#     assert await _filter(admin_message) == True
