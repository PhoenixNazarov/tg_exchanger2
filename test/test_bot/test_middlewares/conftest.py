import asyncio

import pytest
import pytest_asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from bot.database.make_connect import create_db_session
from bot import handlers, middlewares


@pytest_asyncio.fixture(scope="session")
async def local_bot():
    bot = Bot("123123:ASD", parse_mode = "HTML")
    return bot


@pytest_asyncio.fixture(scope="session")
async def local_dp():
    dp = Dispatcher(storage = MemoryStorage())
    dp.update.middleware(middlewares.SessionMiddleware(await create_db_session()))
    return dp
