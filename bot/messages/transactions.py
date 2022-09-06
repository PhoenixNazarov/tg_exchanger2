from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from bot.database.models.transaction_const import TransGet, TransStatus
from bot.info import _


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
