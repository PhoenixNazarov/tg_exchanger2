from aiogram.filters.callback_data import CallbackData

from bot.database.models import TransGet
from bot.info import _


class TransactionChannel(CallbackData, prefix = "mer_channel"):
    id_transaction: int
    take_transaction: bool
    complain_transaction: bool


class ControlTransUser(CallbackData, prefix = "my_trans_user"):
    id_transaction: int

    main: int = 0

    cancel: int = 0  # 1-proof, 2-complain
    edit: int = 0  # 1-list edits, 2-have_amount, 3-rate, 4-get_amount

    message: int = 0  # 1-write, 2-history
    accept: int = 0  # 1-proof, 2-accept

    complain: int = 0  # 1-proof, 2-complain


class ControlTransMerch(CallbackData, prefix = "my_trans_merch"):
    id_transaction: int

    main: int = 0

    message: int = 0  # 1-write, 2-history
    accept: int = 0  # 1-proof, 2-accept

    complain: int = 0  # 1-proof, 2-complain


def text_transaction(transaction: dict, merchant: bool = False, desc: str = '', small: bool = False) -> str:
    text = ''
    if 'id' in transaction:
        text = _('Transaction #{id}\n').format(**transaction)

    if desc:
        text += '🪧 ' + desc + '\n\n'

    if not merchant:
        text += _('🤝 Give: {have_amount} {have_currency}'
                  '\n🤝 Get: {get_amount} {get_currency}'
                  '\n📉 Rate: {rate}').format(**transaction)
    else:
        text += _('🤝 Get: {have_amount} {have_currency}'
                  '\n🤝 Give: {get_amount} {get_currency}'
                  '\n💸 Merchant commission: {commission_merchant} {have_currency}'
                  '\n📉 Rate: {rate}').format(**transaction)

    if 'status' in transaction:
        text += _('\n👔 Status: {status}').format(**transaction)

    if 'receive' in transaction:
        text += _('\n💳 Receipt type: {type_receive_thb}')
        if transaction['type_receive_thb'] == TransGet.cash:
            text += _('\n🏙: {cash_town}, {cash_region}').format(**transaction)
        elif transaction['type_receive_thb'] == TransGet.bank_balance:
            text += _('\n🏦: {bank_name} {bank_number}'
                      '\n👨‍💼: {bank_username}').format(**transaction)

    return text
