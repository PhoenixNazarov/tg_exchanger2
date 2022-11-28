from aiogram.types import BotCommand

from info import _


def get_default_commands(lang: str = 'en') -> list[BotCommand]:
    commands = [
        BotCommand(command = '/start', description = _('start bot', locale=lang)),
        BotCommand(command = '/help', description = _('how it works?', locale=lang)),
        BotCommand(command = '/lang', description = _('change language', locale=lang))
    ]

    return commands
