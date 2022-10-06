from typing import Optional

from aiogram.types import User

from bot.config_reader import config
from bot.database.models import Transaction, Currency, TransStatus, MessageTransaction, TransactionComplain
from bot.database.models import User as UserModel
from bot.utils.calculate_amount import calculate_get_amount
from . import users, transactions, merchants
from .query_controller import QueryController
from ..handlers.errors import MyTgException, ChangeMessage, DelMessage


class BotQueryController:
    def __init__(self, query_controller: QueryController):
        self._query_controller: QueryController = query_controller

        self._user_tg: Optional[User] = None
        self._user: Optional[UserModel] = None

        self._work_transactions: Optional[list[Transaction]] = None

    # Users
    async def get_other_user(self, user_id: int):
        if not self.is_admin():
            raise MyTgException(inline_message = 'Permission denied')
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
        return self._user_tg.id in config.merchants

    def is_admin(self) -> bool:
        return self._user_tg.id in config.admins

    async def add_merchant(self, user_id: int):
        if not self.is_admin():
            raise MyTgException(inline_message = 'Permission denied')
        return await merchants.add_merchant(self._query_controller, user_id)

    async def get_merchants(self):
        if not self.is_admin():
            raise MyTgException(inline_message = 'Permission denied')
        return await merchants.get_merchants(self._query_controller)

    # Transactions
    async def create_transaction(self, data):
        if self.is_merchant():
            raise MyTgException(text_message = 'Merchant cant make transaction')
        if len(await self.get_exchange_transactions()) >= config.max_user_transaction:
            raise MyTgException(text_message = 'You have limit count of your transaction')

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
            raise MyTgException(text_message = 'Merchant cant make transaction')
        if len(await self.get_exchange_transactions()) >= config.max_user_transaction:
            raise MyTgException(text_message = 'You have limit count of your transaction')

        return await transactions.create_transaction(
            self._query_controller,
            user_id = self._user.id,
            **data
        )

    async def set_channel_message_transaction(self, transaction: Transaction, message_id: int):
        return await transactions.update_transaction(self._query_controller, transaction,
                                                     {'merchant_message_id': message_id})

    async def get_transaction(self, transaction_id: int) -> Transaction:
        transaction = await transactions.get_transaction(self._query_controller, transaction_id)
        if self.is_merchant() and transaction.merchant_id is None:
            return transaction
        if (self.is_merchant() and (transaction.merchant_id == self._user.id)) or (
                transaction.user_id == self._user.id):
            return transaction
        raise MyTgException(text_message = 'You can not get this transaction')

    async def get_exchange_transactions(self) -> list[Transaction]:
        if self._work_transactions:
            return self._work_transactions
        self._work_transactions = await transactions.get_work_transaction(self._query_controller, self._user.id,
                                                                          self.is_merchant())
        return self._work_transactions

    async def merchant_take_transaction(self, transaction: Transaction):
        if not self.is_merchant():
            raise MyTgException(inline_message = 'You is not merchant')
        if transaction.status != TransStatus.in_stack:
            raise MyTgException(inline_message = 'Cant take this transaction')
        thb_amount = transaction.get_amount if transaction.get_currency in Currency.change() \
            else transaction.have_amount
        if self._user.merchant.allow_max_amount < thb_amount:
            raise MyTgException(inline_message = 'Too much amount for you')
        if len(await self.get_exchange_transactions()) > 3:  # todo const
            raise MyTgException(inline_message = 'You have too much transactions')

        transaction.merchant_id = self._user.id
        transaction.status = TransStatus.in_exchange
        await transactions.update_transaction(self._query_controller, transaction,
                                              {'status': TransStatus.in_exchange, 'merchant_id': self._user.id})

        return transaction

    async def merchant_get_transaction_money(self, transaction: Transaction):
        if transaction.merchant_id != self._user.id:
            raise DelMessage(inline_message = 'You is not merchant of this transaction')
        if transaction.status != TransStatus.in_exchange:
            raise DelMessage(inline_message = 'Cant accept money for this transaction')
        if transaction.complain:
            raise MyTgException(inline_message = 'Transaction is complain')

        transaction.status = TransStatus.wait_good_user
        await transactions.update_transaction(self._query_controller, transaction,
                                              {'status': TransStatus.wait_good_user})
        return transaction

    async def user_get_transaction_money(self, transaction: Transaction) -> Transaction:
        if transaction.user_id != self._user.id:
            raise DelMessage(inline_message = 'You is not maker of this transaction')
        if transaction.status != TransStatus.wait_good_user:
            raise DelMessage(inline_message = 'Cant accept money for this transaction')
        if transaction.complain:
            raise MyTgException(inline_message = 'Transaction is complain')

        return await transactions.finish_transaction(self._query_controller, transaction, TransStatus.good_finished)

    async def user_cancel_transaction(self, transaction: Transaction) -> Transaction:
        if transaction.user_id != self._user.id:
            raise DelMessage(inline_message = 'You is not maker of this transaction')
        if transaction.status not in [TransStatus.in_stack, TransStatus.in_exchange]:
            raise MyTgException(inline_message = 'You can not cancel this transaction')
        if transaction.complain:
            raise DelMessage(inline_message = 'Transaction is complain')

        return await transactions.finish_transaction(self._query_controller, transaction, TransStatus.canceled)

    async def complain_transaction(self, transaction: Transaction, cause: str) -> TransactionComplain:
        if transaction.complain:
            raise DelMessage(inline_message = 'Already complain')

        return await transactions.create_complain(self._query_controller, transaction,
                                                  transaction.merchant_id == self._user.id, cause)

    async def un_complain_transaction(self, transaction):
        if not transaction.complain:
            raise DelMessage(inline_message = 'Is not complain')
        if (transaction.complain.is_merchant and transaction.merchant_id != self._user.id) and \
                (transaction.user_id != self._user.id):
            raise MyTgException(inline_message = 'Not you complained')

        await transactions.delete_complain(self._query_controller, transaction)

    async def change_transaction(self, transaction, key: str, value: float):
        if transaction.user_id != self._user.id:
            raise DelMessage(inline_message = 'You is not maker of this transaction')
        if transaction.status not in [TransStatus.in_stack, TransStatus.in_exchange]:
            raise DelMessage(inline_message = 'You cant edit this transaction')
        if transaction.complain:
            raise DelMessage(inline_message = 'transaction is complain')

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
            raise DelMessage(inline_message = 'Unknown key')

    async def send_sms_transaction(self, transaction, text: str) -> MessageTransaction:
        if transaction.merchant_id != self._user.id and transaction.user_id != self._user.id:
            raise DelMessage(inline_message = 'You is not merchant or maker of this transaction')
        if transaction.status not in TransStatus.exchange():
            raise DelMessage(inline_message = 'You can not write message for this transaction')
        return await transactions.create_message(self._query_controller, transaction.id, text,
                                                 transaction.merchant_id != self._user.id)

    async def get_sms_history_transaction(self, transaction):
        if transaction.merchant_id != self._user.id and transaction.user_id != self._user.id:
            raise DelMessage(inline_message = 'You is not merchant or maker of this transaction')
        if transaction.status not in TransStatus.exchange():
            raise DelMessage(inline_message = 'You can not write message for this transaction')
        return await transactions.get_messages(self._query_controller, transaction.id)
