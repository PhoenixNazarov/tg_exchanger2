import datetime

from aiogram.types import Message, Chat, User, Update, Contact, CallbackQuery


def get_username(user_id):
    if user_id == 557060775:
        return 'phoenixNazarov'
    return 'asdasdasdasd'


def generate_message(text='', user_id=557060775):
    return Update(
        update_id = 1,

        message = Message(
            message_id = 1,
            date = datetime.datetime(2022, 8, 25, 12, 56, 9, tzinfo = datetime.timezone.utc),
            chat = Chat(id = user_id, type = 'private', username = get_username(user_id), first_name = 'Вова',
                        last_name = 'Назаров'),
            from_user = User(id = user_id, is_bot = False, first_name = 'Вова', last_name = 'Назаров',
                             username = get_username(user_id), language_code = 'ru'),
            text = text
        )
    )


def generate_query(message, data, user_id=557060775):
    return Update(
        update_id = 1,

        callback_query = CallbackQuery(
            id = '2392557814574595461',
            from_user = User(id = user_id, is_bot = False, first_name = 'Вова', last_name = 'Назаров',
                             username = get_username(user_id), language_code = 'ru'),
            chat_instance = "3497100540936108344",
            message = message,
            data = data
        )
    )


def generate_contact(phone='', user_id=557060775):
    return Update(
        update_id = 1,

        message = Message(
            message_id = 1,
            date = datetime.datetime(2022, 8, 25, 12, 56, 9, tzinfo = datetime.timezone.utc),
            chat = Chat(id = user_id, type = 'private', username = get_username(user_id), first_name = 'Вова',
                        last_name = 'Назаров'),
            from_user = User(id = user_id, is_bot = False, first_name = 'Вова', last_name = 'Назаров',
                             username = get_username(user_id), language_code = 'ru'),
            contact = Contact(
                phone_number = phone,
                first_name = 'Вова'
            )
        )
    )
