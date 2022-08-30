from enum import Enum
from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config_reader import config


class PeopleRoles(Enum):
    USER = 0
    MERCHANT = 1
    ADMIN = 2


class PeopleRoleFilter(BaseFilter):
    people_role: Union[PeopleRoles, List[PeopleRoles]]

    async def __get_role(self, _id) -> PeopleRoles:
        if _id in config.admins:
            return PeopleRoles.ADMIN

        if _id:
            pass

        return PeopleRoles.USER

    async def __call__(self, message: Message) -> bool:
        role = await self.__get_role(message.from_user.id)
        if isinstance(self.people_role, PeopleRoles):
            return role == self.people_role
        else:
            return role in self.people_role
