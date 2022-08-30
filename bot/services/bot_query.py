import asyncio
from typing import Optional
from aiogram.types import User

from bot.database.models import User as UserModel
from . import users
from .query_controller import QueryController


class BotQueryController:
    def __init__(self, query_controller: QueryController):
        self._query_controller: QueryController = query_controller

        self._user_tg: Optional[User] = None
        self._user: Optional[UserModel] = None

    def get_user(self):
        return self._user

    async def get_and_update_user(self, user: User):
        self._user_tg = user
        self._user = await users.get_user(self._query_controller, self._user_tg.id)
        if self._user:
            await users.update_user(self._query_controller, self._user, {
                'username': self._user_tg.username,
                'first_name': self._user_tg.first_name,
                'last_name': self._user_tg.last_name
            })

    async def create_user(self) -> UserModel:
        self._user = await users.create_user(self._query_controller, self._user_tg.id,
                                             self._user_tg.first_name,
                                             self._user_tg.last_name,
                                             self._user_tg.username,
                                             self._user_tg.language_code)
        return self._user

    async def set_phone(self, number: str) -> None:
        await users.update_user(self._query_controller, self._user, {
            'phone': number
        })

    async def change_language(self, lang: str) -> None:
        await users.update_user(self._query_controller, self._user, {
            'language': lang
        })
