import random

import names
from aiogram.types import User


def generate_user(user_id=123):
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    username = first_name + '_' + last_name

    return User(id = user_id,
                is_bot = False,
                first_name = first_name,
                last_name = last_name,
                username = username,
                language_code = random.choice(['ru', 'en']))


def change_user(user: User, first_name: str = None, last_name: str = None, username: str = None,
                language_code: str = None):
    if not first_name:
        first_name = user.first_name
    if not last_name:
        last_name = user.last_name
    if not username:
        username = user.username
    if not language_code:
        language_code = user.language_code
    return User(
        id = user.id,
        is_bot = False,
        first_name = first_name,
        last_name = last_name,
        username = username,
        language_code = language_code)
