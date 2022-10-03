from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder, \
    ReplyKeyboardBuilder, KeyboardButton

from bot.database.models import Transaction, TransStatus
from bot.info import _
from bot.messages.transactions import text_transaction, ControlTransMerch, ControlTransUser
from bot.services.bot_query import BotQueryController

router = Router()


class SmsTransMerch(StatesGroup):
    text = State()


def get_main_keyboard(transaction: Transaction) -> KeyboardBuilder[InlineKeyboardButton]:
    if transaction.status == TransStatus.in_exchange:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('✅ Accept'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, cancel = 1).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, complain = 1).pack())
        )
    elif transaction.complain:
        button = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 2).pack()),
        )
        if transaction.complain.merchant_complain:
            button.row(
                InlineKeyboardButton(
                    text = _('⛔ Un complain'),
                    callback_data = ControlTransUser(id_transaction = transaction.id, complain = -1).pack())
            )
        return button
    elif transaction.status == TransStatus.wait_good_user:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, complain = 1).pack())
        )


async def send_transaction(message: Message, transaction: Transaction):
    await message.answer(
        text = text_transaction(await transaction.to_json(), merchant = True),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.message(Command(commands = 'mytrans'))
async def get_transactions(message: Message, bot_query: BotQueryController):
    transactions = await bot_query.get_exchange_transactions()
    return [await send_transaction(message, trans) for trans in transactions]


@router.callback_query(ControlTransMerch.filter(F.main == 1))
async def get_transaction(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                          bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), merchant = True),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.message == 1))
async def write_message(callback_query: CallbackQuery, callback_data: ControlTransMerch, bot_query: BotQueryController,
                        state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await state.set_state(SmsTransMerch.text)
    await state.update_data(id_transaction = callback_data.id_transaction)
    await callback_query.message.delete()
    await callback_query.message.answer(
        text = text_transaction(await transaction.to_json(), desc = _("Write your messages"), merchant = True,
                                small = True),
        reply_markup = ReplyKeyboardBuilder().row(KeyboardButton(text = _('ℹ Back'))).as_markup(resize_keyboard = True)
    )


@router.message(SmsTransMerch.text)
async def get_message(message: Message, bot_query: BotQueryController, state: FSMContext, bot: Bot):
    transaction: Transaction = await bot_query.get_transaction((await state.get_data())['id_transaction'])

    if message.text == _('ℹ Back'):
        await state.clear()
        return await send_transaction(message, transaction)

    message = await bot_query.send_sms_transaction(transaction, message.text)
    await bot.send_message(
        chat_id = transaction.user_id,
        text = text_transaction(await transaction.to_json(), desc = _('New message\n {text}').format(text = message.text),
                                small = True),
        reply_markup = InlineKeyboardBuilder()
        .row(
            InlineKeyboardButton(text = '✉️ Answer',
                                 callback_data = ControlTransUser(id_transaction = transaction.id, message = 1).pack()))
        .row(
            InlineKeyboardButton(text = 'ℹ Transaction',
                                 callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack()))
        .as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.message == 2))
async def history_messages(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                           bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    messages = await bot_query.get_sms_history_transaction(transaction)

    text = '\n'.join(
        [_('Merchant: {text}').format(text = i.text) if i.from_merchant else _('Maker: {text}').format(text = i.text)
         for i in messages])
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), merchant = True, desc = _("Message history:\n{messages}")
                                .format(messages = text), small = True),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(text = _('ℹ Back'),
                                 callback_data = ControlTransMerch(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.accept == 1))
async def accept(callback_query: CallbackQuery, callback_data: ControlTransMerch, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), merchant = True,
                                desc = _("Do you want accept transaction?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('✅ Yes'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, accept = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('❌ No'),
                callback_data = ControlTransMerch(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.accept == 2))
async def accept_proof(callback_query: CallbackQuery, callback_data: ControlTransMerch, bot_query: BotQueryController,
                       bot: Bot):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    transaction = await bot_query.merchant_get_transaction_money(transaction)

    await get_transaction(callback_query, callback_data, bot_query)

    await bot.send_message(
        chat_id = transaction.user_id,
        text = text_transaction(await transaction.to_json(), desc = _('Merchant confirmed transfer')),
        reply_markup = InlineKeyboardBuilder()
        .row(
            InlineKeyboardButton(text = '✅ Accept',
                                 callback_data = ControlTransUser(id_transaction = transaction.id, accept = 1).pack()))
        .row(
            InlineKeyboardButton(text = 'ℹ Transaction',
                                 callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack()))
        .as_markup()
    )

    return transaction


@router.callback_query(ControlTransMerch.filter(F.complain == 1))
async def complain_list(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                        bot_query: BotQueryController):
    # todo
    return
    #
    # transaction = await bot_query.get_transaction(callback_data.id_transaction)
    #
    # await bot_query.user_get_transaction_money(transaction)
    # await get_transaction(callback_query, callback_data, bot_query)
