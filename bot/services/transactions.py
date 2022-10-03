from typing import Optional

from bot.database import (
    Transaction, RequisitesCash, RequisitesBankBalance,
    TransGet, TransStatus, MessageTransaction, TransactionComplain)
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
        return await session(Transaction).get_models_filter({'merchant_id': user_id, 'active': True})
    return await session(Transaction).get_models_filter({'user_id': user_id, 'active': True})


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
                             finish_status: TransStatus) -> Transaction:
    if finish_status not in TransStatus.end():

        raise Exception('Cant finish transaction')  # todo exception
    await session(transaction).update_model_values({
        'status': finish_status,
        'active': False
    })
    return transaction


async def create_complain(session: QueryController, transaction: Transaction, is_merchant: bool, cause: str):
    complain = TransactionComplain(merchant_complain=is_merchant, cause = cause)
    await session(complain).add_model()
    await session(transaction).update_model_values({
        'complain_id': complain.id,
    })


async def delete_complain(session: QueryController, transaction: Transaction):
    await session(transaction.complain).delete_model()
    await session(transaction).update_model_values({
        'complain_id': 0,
    })
