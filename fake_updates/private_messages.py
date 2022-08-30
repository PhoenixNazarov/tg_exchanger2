import datetime

from aiogram.types import Message, Chat, User, Update


def generate_message(text='', user_id=123):
    return Update(
        update_id = 1,

        message = Message(
            message_id = 1,
            date = datetime.datetime(2022, 8, 25, 12, 56, 9, tzinfo = datetime.timezone.utc),
            chat = Chat(id = user_id, type = 'private', username = 'phoenixNazarov', first_name = 'Вова',
                        last_name = 'Назаров'),
            from_user = User(id = user_id, is_bot = False, first_name = 'Вова', last_name = 'Назаров',
                             username = 'phoenixNazarov', language_code = 'ru'),
            text = text
        )
    )
