from aiogram import Router

from . import request

router = Router()
router.include_router(request.router)
