from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles


router = Router()
router.message.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))
router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.MERCHANT))

