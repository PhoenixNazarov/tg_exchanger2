from aiogram import Router

from . import private, channel

router = Router()

router.include_router(channel.router)
router.include_router(private.router)
