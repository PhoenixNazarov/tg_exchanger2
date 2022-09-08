import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from bot.config_reader import config

from bot.database.make_connect import create_db_session

bot = Bot(config.bot_token.get_secret_value(), parse_mode = "HTML")

# STORAGE
if config.fsm_mode == "redis" and not config.test:
    storage = RedisStorage.from_url(
        url = config.redis
    )
else:
    storage = MemoryStorage()


from bot import handlers, middlewares

# HANDLERS
dp = Dispatcher(storage = storage)
dp.include_router(handlers.router)


# MIDDLEWARES
async def load_db():
    dp.update.middleware(middlewares.SessionMiddleware(await create_db_session()))
# asyncio.run(load_db())
