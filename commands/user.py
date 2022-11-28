from aiogram import Bot
from aiogram.types import BotCommandScopeChat, BotCommand

from info import _
from .default import get_default_commands


def get_user_commands(lang: str = 'en') -> list[BotCommand]:
    commands = get_default_commands(lang)

    commands.extend([
        BotCommand(command = '/newtrans', description = _('create new transaction', locale = lang)),
        BotCommand(command = '/mytrans', description = _('show my transactions', locale = lang)),
    ])

    return commands


async def set_user_commands(bot: Bot, user_id: int, commands_lang: str):
    await bot.set_my_commands(get_user_commands(commands_lang), scope = BotCommandScopeChat(chat_id = user_id))
