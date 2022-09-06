from typing import Optional

from aiogram.types import User

from bot.config_reader import config
from bot.database.models import Transaction, Currency, TransStatus
from bot.database.models import User as UserModel
from bot.utils.calculate_amount import calculate_get_amount
from . import users, transactions, merchants
from .query_controller import QueryController


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
            raise Exception('permission denied')  # todo exception
        return await merchants.add_merchant(self._query_controller, user_id)

    async def get_merchants(self):
        if not self.is_admin():
            raise Exception('permission denied')  # todo exception
        return await merchants.get_merchants(self._query_controller)

    # Transactions
    async def create_transaction(self, data):
        if self.is_merchant():
            raise Exception('Merchant cant make transaction')  # todo exception
        if len(self._user.transactions) >= config.max_user_transaction:
            raise Exception('You have limit count of your transaction')  # todo exception

        out = {
            'have_amount': data['amount'],
            'get_amount': calculate_get_amount(data['have_currency'], data['get_currency'],
                                               data['amount'], data['rate']),
            'commission_merchant': round(data['amount'] * config.merchant_commission, 2),
            'commission_user': 0
        }

        return out

    async def public_transaction(self, data: dict) -> Transaction:
        if self.is_merchant():
            raise Exception('Merchant cant make transaction')  # todo exception
        if len(self._user.transactions) >= config.max_user_transaction:
            raise Exception('You have limit count of your transaction')  # todo exception

        return await transactions.create_transaction(
            self._query_controller,
            user_id = self._user.id,
            **data
        )

    async def set_channel_message_transaction(self, transaction: Transaction, message_id: int):
        return await transactions.update_transaction(self._query_controller, transaction,
                                                     {'merchant_message_id': message_id})

    async def get_transaction(self, transaction_id: id) -> Optional[Transaction]:
        transaction = await transactions.get_transaction(self._query_controller, transaction_id)
        if (self.is_merchant() and transaction.merchant_id == self._user.id) or (transaction.user_id == self._user.id):
            return transaction

    async def get_exchange_transactions(self) -> list[Transaction]:
        return await transactions.get_work_transaction(self._query_controller, self._user.id, self.is_merchant())

    async def merchant_take_transaction(self, transaction: Transaction):
        if self.is_merchant():
            raise Exception('You is not merchant')  # todo exception
        if transaction.status != TransStatus.in_stack:
            raise Exception('Cant take this transaction')  # todo exception
        thb_amount = transaction.get_amount if transaction.get_currency in Currency.change() \
            else transaction.have_amount
        if self._user.merchant.allow_max_amount < thb_amount:
            raise Exception('Too much amount for you')  # todo exception
        if len(self._user.merchant.transactions) > 3:  # todo const
            raise Exception('You have too much transactions')  # todo exception

        transaction.merchant_id = self._user.id
        transaction.status = TransStatus.in_exchange
        return transaction

    async def merchant_get_transaction_money(self, transaction: Transaction):
        if transaction.merchant_id != self._user.id:
            raise Exception('You is not merchant of this transaction')  # todo exception
        if transaction.status != TransStatus.in_exchange:
            raise Exception('Cant accept money for this transaction')  # todo exception
        transaction.status = TransStatus.wait_good_user
        return transaction

    async def user_get_transaction_money(self, transaction):
        if transaction.user_id != self._user.id:
            raise Exception('You is not maker of this transaction')  # todo exception
        if transaction.status != TransStatus.wait_good_user:
            raise Exception('Cant accept money for this transaction')  # todo exception
        return await transactions.finish_transaction(self._query_controller, transaction, TransStatus.good_finished)

    async def user_cancel_transaction(self, transaction):
        if transaction.user_id != self._user.id:
            raise Exception('You is not maker of this transaction')  # todo exception
        if transaction.status not in [TransStatus.in_stack, TransStatus.in_exchange]:
            raise Exception('You can not cancel this transaction')  # todo exception

        return await transactions.finish_transaction(self._query_controller, transaction, TransStatus.canceled)

    async def complain_transaction(self, transaction):
        # todo
        pass

    async def change_transaction(self, transaction, key: str, value: float):
        if transaction.user_id != self._user.id:
            raise Exception('You is not maker of this transaction')  # todo exception
        if transaction.status not in [TransStatus.in_stack, TransStatus.in_exchange]:
            raise Exception('You can edit this transaction')  # todo exception

        if key == 'have_amount':
            return await transactions.update_transaction(
                self._query_controller, transaction,
                {
                    'have_amount': value,
                    'get_amount': calculate_get_amount(transaction.have_currency,
                                                       transaction.get_currency,
                                                       value, transaction.rate),
                    'commission_merchant': round(
                        value * config.merchant_commission, 2),
                    'commission_user': 0
                })
        elif key == 'rate':
            return await transactions.update_transaction(
                self._query_controller, transaction,
                {
                    'rate': value,
                    'get_amount': calculate_get_amount(transaction.have_currency,
                                                       transaction.get_currency,
                                                       transaction.have_amount, value),
                })

        elif key == 'get_amount':
            new_amount = calculate_get_amount(transaction.get_currency, transaction.have_currency,
                                              value, transaction.rate)
            return await transactions.update_transaction(
                self._query_controller, transaction,
                {
                    'have_amount': new_amount,
                    'get_amount': value,
                    'commission_merchant': round(
                        new_amount * config.merchant_commission, 2),
                    'commission_user': 0
                })
        else:
            raise Exception('Unknown key')  # todo exception

    async def send_sms_transaction(self, transaction, text: str):
        if transaction.merchant_id != self._user.id or transaction.user_id != self._user.id:
            raise Exception('You is not merchant or maker of this transaction')  # todo exception
        if transaction.status not in TransStatus.exchange():
            raise Exception('You can not write message for this transaction')  # todo exception
        return await transactions.create_message(self._query_controller, transaction.id, text,
                                                 transaction.merchant_id != self._user.id)

    async def get_sms_history_transaction(self, transaction):
        if transaction.merchant_id != self._user.id or transaction.user_id != self._user.id:
            raise Exception('You is not merchant or maker of this transaction')  # todo exception
        if transaction.status not in TransStatus.exchange():
            raise Exception('You can not write message for this transaction')  # todo exception
        return await transactions.get_messages(self._query_controller, transaction.id)
