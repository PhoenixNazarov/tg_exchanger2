from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.info import _  # todo delete
from bot.services.bot_query import BotQueryController

from bot.commands import set_user_commands, set_merchant_commands, set_admin_commands


router = Router()


class LanguageCallback(CallbackData, prefix = "set_lang"):
    lang: str


@router.message(Command(commands = ['lang']))
async def change_language(message: Message):
    await message.answer(
        text = _('Choose the language'),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(text = _('🇷🇺 ru'),
                                 callback_data = LanguageCallback(lang = 'ru').pack()),
            InlineKeyboardButton(text = _('🇺🇸 en'),
                                 callback_data = LanguageCallback(lang = 'en').pack())
        ).as_markup()
    )


@router.callback_query(LanguageCallback.filter())
async def set_language(query: CallbackQuery, callback_data: LanguageCallback, bot_query: BotQueryController, bot: Bot):
    await bot_query.change_language(callback_data.lang)
    await bot.edit_message_text(chat_id = query.message.chat.id, message_id = query.message.message_id,
                                text = _('Language have been set on: {new_lang}').format(new_lang = callback_data.lang),
                                reply_markup = InlineKeyboardBuilder().as_markup())
    if bot_query.is_merchant():
        await set_merchant_commands(bot, bot_query.get_user().id, callback_data.lang)
    elif bot_query.is_admin():
        await set_admin_commands(bot, bot_query.get_user().id, callback_data.lang)
    else:
        await set_user_commands(bot, bot_query.get_user().id, callback_data.lang)
