from aiogram import Router, F
from bot.filters.people_role import PeopleRoleFilter, PeopleRoles

from . import make_transaction, registration, home, transaction

router = Router()
router.message.filter(PeopleRoleFilter(people_role = PeopleRoles.USER))
router.callback_query.filter(PeopleRoleFilter(people_role = PeopleRoles.USER))

router.include_router(registration.router)
router.include_router(home.router)
router.include_router(make_transaction.router)
router.include_router(transaction.router)
