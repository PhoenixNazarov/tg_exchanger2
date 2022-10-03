import asyncio
import logging

from bot.loader import dp, bot

from bot import middlewares
from bot.config_reader import config
from bot.database.make_connect import create_db_session


# from bot.handlers import default_commands, spin
# from bot.middlewares.throttling import ThrottlingMiddleware
# from bot.ui_commands import set_bot_commands


async def main():
    if config.debug:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.WARNING)

    dp.update.middleware(middlewares.SessionMiddleware(await create_db_session()))

    try:
        await dp.start_polling(bot, allowed_updates = dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
