import asyncio
from typing import Optional
from aiogram.types import User

from bot.database.models import User as UserModel
from bot.database.models import Transaction
from . import users, transactions, merchants
from .query_controller import QueryController

from bot.config_reader import config


class BotQueryController:
    def __init__(self, query_controller: QueryController):
        self._query_controller: QueryController = query_controller

        self._user_tg: Optional[User] = None
        self._user: Optional[UserModel] = None

    # Users
    async def get_other_user(self, user_id: int):
        if not self.is_admin():
            raise Exception('permission denied')
        return await users.get_user(self._query_controller, user_id)

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

    # Merchants
    def is_merchant(self) -> bool:
        return self._user.id in config.merchants

    def is_admin(self) -> bool:
        return self._user.id in config.admins

    async def add_merchant(self, user_id: int):
        if not self.is_admin():
            raise Exception('permission denied')
        return await merchants.add_merchant(self._query_controller, user_id)

    async def get_merchants(self):
        if not self.is_admin():
            raise Exception('permission denied')
        return await merchants.get_merchants(self._query_controller)

    # Transactions
    async def create_transaction(self, data):
        if self.is_merchant():
            raise Exception('Merchant cant make transaction')
        if len(self._user.transactions) >= config.max_user_transaction:
            raise Exception('You have limit count of your transaction')

        return await transactions.create_transaction(self._query_controller, self._user.id, data)

    async def get_transaction(self, transaction_id: id) -> Optional[Transaction]:
        transaction = await transactions.get_transaction(self._query_controller, transaction_id)
        if (self.is_merchant() and transaction.merchant_id == self._user.id) or (transaction.user_id == self._user.id):
            return transaction

    async def merchant_take_transaction(self, transaction: Transaction):
        if self.is_merchant():
            raise Exception('You is not merchant')
        # todo
        pass

    async def merchant_get_transaction_money(self, transaction: Transaction):
        if transaction.merchant.id != self._user.id:
            raise Exception('You is not merchant of this transaction')
        # todo
        pass

    async def user_get_transaction_money(self, transaction):
        if transaction.user.id != self._user.id:
            raise Exception('You is not maker of this transaction')
        # todo
        pass

    async def user_cancel_transaction(self, transaction):
        # todo
        pass

    async def complain_transaction(self, transaction):
        # todo
        pass

    async def change_transaction(self, transaction):
        # todo
        pass

    async def send_sms_transaction(self, transaction):
        # todo
        pass

