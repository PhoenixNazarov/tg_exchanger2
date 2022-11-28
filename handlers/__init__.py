from aiogram import Router
from . import users
from . import merchants
from . import errors
from . import free_messages

router = Router()

router.include_router(errors.router)

router.include_router(merchants.router)
router.include_router(users.router)
router.include_router(free_messages.router)

router.include_router(users.home.outer_router)
