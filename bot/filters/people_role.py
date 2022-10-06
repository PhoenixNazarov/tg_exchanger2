from enum import Enum
from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.config_reader import config

from bot.handlers.errors import MyTgException


class PeopleRoles(Enum):
    USER = 0
    MERCHANT = 1
    ADMIN = 2


class PeopleRoleFilter(BaseFilter):
    people_role: Union[PeopleRoles, List[PeopleRoles]]

    async def __get_roles(self, _id) -> List[PeopleRoles]:
        roles = []
        if _id in config.admins:
            roles.append(PeopleRoles.ADMIN)

        if _id in config.merchants:
            roles.append(PeopleRoles.MERCHANT)
        else:
            roles.append(PeopleRoles.USER)

        return roles

    async def __call__(self, update: Union[Message, CallbackQuery]) -> bool:
        if isinstance(update, Message):
            user_id = update.from_user.id
        elif isinstance(update, CallbackQuery):
            user_id = update.from_user.id
        else:
            raise MyTgException(inline_message = "Cant find your id")

        roles = await self.__get_roles(user_id)
        if isinstance(self.people_role, PeopleRoles):
            return self.people_role in roles
        else:
            return any(i in self.people_role for i in roles)
