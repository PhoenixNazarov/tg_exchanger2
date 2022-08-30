from sqlalchemy import select, update, or_

from bot.database import (
    Transaction, RequisitesCash, RequisitesBankBalance, TransactionModerate,
    TransGet, TransStatus, MessageTransaction)
from bot.utils.misc.save_execute import *
from .query_controller import QueryController


class TransactionQueryController(QueryController):
    _model: Transaction

    def add_moderate_transaction(self, model: TransactionModerate):


# async def get_work_transactions(session: AsyncSession, user_id) -> Transaction:
#     sql = select(Transaction).where(or_(Transaction.user_id == user_id)).where(
#         or_(Transaction.status == TransStatus.in_stack,
#             Transaction.status == TransStatus.in_exchange,
#             Transaction.status == TransStatus.wait_good_user))
#     query = await session.execute(sql)
#
#     user = query.all()
#
#     return user


async def create_pre_transaction(session: AsyncSession, data, user) -> TransactionModerate:
    trans = TransactionModerate(
        amount = data['amount'],
        have_currency = data['have_currency'],
        get_currency = data['get_currency'],
        rate = data['rate'],
        auth_user = user.auth
    )

    trans.user_id = user.id
    trans.get_thb_type = data['type_get_thb']
    if trans.get_thb_type == TransGet.cash:
        trans.option1 = data['town']
        trans.option2 = data['region']
    elif trans.get_thb_type == TransGet.atm_machine:
        pass
    elif trans.get_thb_type == TransGet.bank_balance:
        trans.option1 = data['bank']
        trans.option2 = data['number']
        trans.option3 = data['name']

    session.add(trans)
    await save_commit(session)
    return trans


async def get_transaction_moderate(session: AsyncSession, _id) -> TransactionModerate:
    sql = select(TransactionModerate).where(TransactionModerate.id == _id)
    query = await session.execute(sql)

    user = query.scalar_one_or_none()

    return user


async def create_transaction(transaction_moderate: TransactionModerate) -> Transaction:
    transaction: Transaction = Transaction(
        user_id = transaction_moderate.user_id,
        have_amount = transaction_moderate.have_amount,
        have_currency = transaction_moderate.have_currency,
        get_amount = transaction_moderate.get_amount,
        get_currency = transaction_moderate.get_currency,
        rate = transaction_moderate.rate,
        commission_user = transaction_moderate.commission_user,
        commission_merchant = transaction_moderate.commission_merchant,
        get_thb_type = transaction_moderate.get_thb_type,
    )
    return transaction


async def create_transaction_receive(transaction: Transaction,
                                     transaction_moderate: TransactionModerate) -> Transaction:
    if transaction.get_thb_type == TransGet.cash:
        return RequisitesCash(
            transaction_id = transaction.id,
            town = transaction_moderate.option1,
            region = transaction_moderate.option2
        )
    elif transaction.get_thb_type == TransGet.bank_balance:
        return RequisitesBankBalance(
            transaction_id = transaction.id,
            bank_name = transaction_moderate.option1,
            number = int(transaction_moderate.option2),
            name = transaction_moderate.option3,
        )


async def un_public_transaction(session: AsyncSession, transaction_moderate: TransactionModerate):
    await session.delete(transaction_moderate)
    await save_commit(session)


async def public_transaction_db(session: AsyncSession, transaction_moderate: TransactionModerate) -> Transaction:
    transaction = await create_transaction(transaction_moderate)

    session.add(transaction)
    await save_commit(session)

    receive = await create_transaction_receive(transaction, transaction_moderate)
    if receive:
        session.add(receive)
        await save_commit(session)

    await session.delete(transaction_moderate)
    await save_commit(session)

    return transaction


async def transaction_set_merchant_message(session: AsyncSession, transaction: Transaction, _id) -> Transaction:
    sql = update(Transaction).where(Transaction.id == transaction.id).values(merchant_message_id = _id)
    await session.execute(sql)

    await save_commit(session)
    return transaction


async def update_status_transaction(session: AsyncSession, transaction: Transaction,
                                    status: TransStatus) -> Transaction:
    sql = update(Transaction).where(Transaction.id == transaction.id).values(status = status)
    await session.execute(sql)

    await save_commit(session)
    return transaction


async def update_value_transaction(session: AsyncSession, transaction: Transaction,
                                   status: TransStatus) -> Transaction:
    sql = update(Transaction).where(Transaction.id == transaction.id).values(status = status)
    await session.execute(sql)

    await save_commit(session)
    return transaction


async def get_transaction_place_line(session: AsyncSession, transaction: Transaction):
    position = 0
    sql = select(Transaction).filter(Transaction.have_currency == transaction.have_currency).filter(
        Transaction.get_currency == transaction.get_currency).filter(
        or_(Transaction.status == TransStatus.in_stack,
            Transaction.status == TransStatus.in_exchange))
    all_models = await session.execute(sql)

    for trans in all_models:
        position += 1
        if trans.id == transaction.id:
            return position


async def create_message(session: AsyncSession, transaction: Transaction, text, from_merchant) -> MessageTransaction:
    message = MessageTransaction(text = text, transaction_id = transaction.id, from_merchant = from_merchant)
    session.add(message)

    save_commit(session)
