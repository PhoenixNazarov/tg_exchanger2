from aiogram import Router, F

from . import users, admins, language

router = Router()

router.message.filter(F.chat.type == 'private')
router.callback_query.filter(F.message.chat.type == 'private')

router.include_router(language.router)
router.include_router(admins.router)
router.include_router(users.router)
