from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles

from . import home

router = Router()
router.message.filter(PeopleRoleFilter(people_role = PeopleRoles.ADMIN))
router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.ADMIN))

router.include_router(home.router)
