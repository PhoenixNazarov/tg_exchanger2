from aiogram import Router, F

router = Router()
router.message.filter(F.chat.type == "channel")
router.callback_query.filter(F.chat.type == "channel")
