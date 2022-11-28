from aiogram import Bot
from aiogram.types import BotCommandScopeChat, BotCommand

from info import _
from .default import get_default_commands


def get_admin_commands(lang: str = 'en') -> list[BotCommand]:
    commands = get_default_commands(lang)

    commands.extend([
        BotCommand(command = '/admin_help', description = _('admin help', locale=lang)),
        BotCommand(command = '/add_merch', description = _('add merchants', locale=lang)),
        BotCommand(command = '/del_merch', description = _('delete merchants', locale=lang)),
        BotCommand(command = '/list_merch', description = _('list merchants', locale=lang)),
        BotCommand(command = '/set_limit_amount', description = _('set maximum amount for merchant\'s deal', locale=lang)),
        BotCommand(command = '/set_accumulated_commission', description = _('change merchant\'s commission', locale=lang)),
    ])

    return commands


async def set_admin_commands(bot: Bot, user_id: int, commands_lang: str):
    await bot.set_my_commands(get_admin_commands(commands_lang), scope=BotCommandScopeChat(chat_id = user_id))
