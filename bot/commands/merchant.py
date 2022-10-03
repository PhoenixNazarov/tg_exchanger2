from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat, BotCommand

from bot.info import _
from .default import get_default_commands


def get_merchant_commands(lang: str = 'en') -> list[BotCommand]:
    commands = get_default_commands(lang)

    commands.extend([
        BotCommand(command = '/mytrans', description = _('show my transactions', locale = lang)),
    ])

    return commands


async def set_merchant_commands(bot: Bot, user_id: int, commands_lang: str):
    await bot.set_my_commands(get_merchant_commands(commands_lang), scope = BotCommandScopeChat(chat_id = user_id))
