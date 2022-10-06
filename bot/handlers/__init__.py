from aiogram import Router

from . import private, channel, errors

router = Router()

router.include_router(errors.router)
router.include_router(channel.router)
router.include_router(private.router)
