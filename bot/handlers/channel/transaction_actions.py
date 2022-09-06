from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from bot.info import _
from bot.loader import bot
from bot.messages.transactions import text_transaction
from bot.services.bot_query import BotQueryController

router = Router()


class TransactionCallback(CallbackData, prefix = "mer_channel"):
    id_transaction: int
    take_transaction: bool
    complain_transaction: bool


@router.callback_query(TransactionCallback.filter())
async def welcome(callback_query: CallbackQuery, callback_data: TransactionCallback, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    if callback_data.take_transaction:
        await bot_query.merchant_take_transaction(transaction)

        await callback_query.message.answer(
            text = text_transaction(await transaction.to_json(), True),
            reply_markup = ReplyKeyboardRemove()  # todo keyboard
        )
        await bot.send_message(
            chat_id = transaction.user_id,
            text = text_transaction(await transaction.to_json(), desc = _('Start exchange')),
            reply_markup = ReplyKeyboardRemove()  # todo keyboard
        )
