from aiogram import Bot, Router
from aiogram.types import Update

router = Router()


class MyTgException(Exception):
    def __init__(self, text_message: str = None, inline_message: str = None):
        self.text_message = text_message
        self.inline_message = inline_message


class DelMessage(MyTgException):
    pass


class ChangeMessage(MyTgException):
    def __init__(self, new_text: str, **kwargs):
        self.new_text = new_text
        super(ChangeMessage, self).__init__(**kwargs)


@router.errors()
async def error_handle(update: Update, exception, bot: Bot):
    callback_query = None
    if update.message is not None:
        message = update.message
    elif update.callback_query is not None:
        callback_query = update.callback_query
        message = update.callback_query.message
    else:
        return

    if isinstance(exception, DelMessage):
        await message.delete()

    if isinstance(exception, ChangeMessage):
        await message.edit_text(exception.new_text)

    if isinstance(exception, MyTgException):
        if exception.text_message is not None:
            await message.answer(exception.text_message)

        if exception.inline_message is not None:
            if callback_query is not None:
                await callback_query.answer(exception.inline_message)
            else:
                await message.answer(exception.inline_message)
