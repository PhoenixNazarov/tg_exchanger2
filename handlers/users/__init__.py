from aiogram import Router

from . import home
from . import bid
from . import request


router = Router()
router.include_router(home.router)
router.include_router(bid.router)
router.include_router(request.router)
