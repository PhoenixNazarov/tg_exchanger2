from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles
from bot.config_reader import config


router = Router()
router.callback_query.filter(F.chat.type == "channel")
router.callback_query.filter(F.chat.id == config.merchant_channel)

router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))

