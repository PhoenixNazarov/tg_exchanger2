from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.info import _
from bot.loader import bot
from bot.messages.transactions import TransactionChannel
from bot.messages.transactions import text_transaction
from bot.services.bot_query import BotQueryController

router = Router()


@router.callback_query(TransactionChannel.filter())
async def welcome(callback_query: CallbackQuery, callback_data: TransactionChannel, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    if transaction is None:
        raise Exception('Transaction is not found')  # todo exception

    if callback_data.take_transaction:
        await bot_query.merchant_take_transaction(transaction)

        merchant_message = await bot.send_message(
            chat_id = transaction.merchant_id,
            text = text_transaction(await transaction.to_json(), merchant = True, desc = _('Start exchange'), ),
            reply_markup = InlineKeyboardBuilder().as_markup()  # todo keyboard
        )
        user_message = await bot.send_message(
            chat_id = transaction.user_id,
            text = text_transaction(await transaction.to_json(), desc = _('Start exchange')),
            reply_markup = InlineKeyboardBuilder().as_markup()  # todo keyboard
        )

        await callback_query.message.edit_text(
            text = callback_query.message.text + _('\n\n Merchant @{merchant_username}').format(
                merchant_username = transaction.merchant.user.username,
                merchant_id = transaction.merchant_id),
            reply_markup = InlineKeyboardBuilder().as_markup()  # todo keyboard
        )

        return merchant_message, user_message
