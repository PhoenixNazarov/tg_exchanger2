from aiogram import Router

from . import request
from . import rate

router = Router()
router.include_router(request.router)
router.include_router(rate.router)
