from typing import Optional

from bot.database import (
    Transaction, TransactionArchive, RequisitesCash, RequisitesBankBalance,
    TransGet, TransStatus, MessageTransaction)
from .query_controller import QueryController


async def create_transaction(session: QueryController,
                             user_id,
                             have_currency, have_amount,
                             get_currency, get_amount,
                             rate,
                             commission_user, commission_merchant,
                             type_receive_thb, **kwargs) -> Transaction:
    transaction = Transaction(
        user_id = user_id,
        have_currency = have_currency,
        have_amount = have_amount,
        get_currency = get_currency,
        get_amount = get_amount,
        rate = rate,
        commission_user = commission_user,
        commission_merchant = commission_merchant,
        get_thb_type = type_receive_thb,
    )
    await session(transaction).add_model()

    if type_receive_thb == TransGet.bank_balance:
        req = RequisitesBankBalance(
            transaction_id = transaction.id,
            bank_name = kwargs['bank_name'],
            number = kwargs['bank_number'],
            name = kwargs['bank_username']
        )
        await session(req).add_model()
    elif type_receive_thb == TransGet.cash:
        req = RequisitesCash(
            transaction_id = transaction.id,
            town = kwargs['cash_town'],
            region = kwargs['cash_region']
        )
        await session(req).add_model()
    return transaction


async def get_transaction(session: QueryController, transaction_id: int) -> Optional[Transaction]:
    return await session(Transaction).get_model(transaction_id)


async def get_work_transaction(session: QueryController, user_id: int, merchant: bool) -> list[Transaction]:
    if merchant:
        return await session(Transaction).get_models_filter({'merchant_id': user_id})
    return await session(Transaction).get_models_filter({'user_id': user_id})


async def update_transaction(session: QueryController, transaction: Transaction, data: dict) -> Transaction:
    await session(transaction).update_model_values(data)
    return transaction


async def create_message(session: QueryController, transaction_id: int, text: str,
                         from_merchant: bool) -> MessageTransaction:
    message = MessageTransaction(
        transaction_id = transaction_id,
        text = text,
        from_merchant = from_merchant
    )
    await session(message).add_model()
    return message


async def get_messages(session: QueryController, transaction_id: int) -> list[MessageTransaction]:
    return await session(MessageTransaction).get_models_filter({'transaction_id': transaction_id})


async def finish_transaction(session: QueryController, transaction: Transaction,
                             finish_status: TransStatus) -> TransactionArchive:
    if finish_status not in TransStatus.end():
        raise Exception('Cant finish transaction')  # todo exception

    archive_transaction = TransactionArchive()
    archive_transaction.user_id = transaction.user_id
    archive_transaction.merchant_id = transaction.merchant_id
    archive_transaction.end_status = finish_status
    archive_transaction.have_amount = transaction.have_amount
    archive_transaction.have_currency = transaction.have_currency
    archive_transaction.get_amount = transaction.get_amount
    archive_transaction.get_currency = transaction.get_currency
    archive_transaction.rate = transaction.rate
    archive_transaction.commission_user = transaction.commission_user
    archive_transaction.commission_merchant = transaction.commission_merchant
    archive_transaction.get_thb_type = transaction.get_thb_type

    await session(archive_transaction).add_model()

    if transaction.get_thb_type == TransGet.bank_balance:
        transaction.req_bank.transaction_archive_id = archive_transaction.id
        transaction.req_bank.transaction_id = None
    elif transaction.get_thb_type == TransGet.cash:
        transaction.req_cash.transaction_archive_id = archive_transaction.id
        transaction.req_cash.transaction_id = None

    await session(transaction).delete_model()
    return archive_transaction
