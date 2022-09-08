from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles
from bot.config_reader import config

from . import transaction_actions

router = Router()
router.callback_query.filter(F.message.chat.type == "channel")
router.callback_query.filter(F.message.chat.id == config.merchant_channel)

router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))

router.include_router(transaction_actions.router)
