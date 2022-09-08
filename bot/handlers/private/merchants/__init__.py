from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles

from . import transaction

router = Router()
router.message.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))
router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))

router.include_router(transaction.router)
