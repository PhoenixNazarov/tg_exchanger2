from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder, \
    ReplyKeyboardBuilder, KeyboardButton

from bot.database.models import Transaction, TransStatus
from bot.info import _
from bot.messages.transactions import text_transaction
from bot.services.bot_query import BotQueryController

router = Router()


class ControlTransMerch(CallbackData, prefix = "my_trans_user"):
    id_transaction: int

    main: int = 0

    message: int = 0  # 1-write, 2-history
    accept: int = 0  # 1-proof, 2-accept

    complain: int = 0  # 1-proof, 2-complain


class SmsTrans(StatesGroup):
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
        text = text_transaction(transaction, merchant = True),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.message(Command(commands = '/mytrans'))
async def get_transactions(message: Message, bot_query: BotQueryController):
    transactions = await bot_query.get_exchange_transactions()
    for trans in transactions:
        await send_transaction(message, trans)


@router.callback_query(ControlTransMerch.filter(F.main == 1))
async def get_transaction(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                          bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(transaction, merchant = True),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.message == 1))
async def write_message(callback_query: CallbackQuery, callback_data: ControlTransMerch, bot_query: BotQueryController,
                        state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.user_cancel_transaction(transaction)
    await state.set_state(SmsTrans.text)
    await state.update_data(id_transaction = callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(transaction, merchant = True, desc = _("Write your messages"), small = True),
        reply_markup = ReplyKeyboardBuilder().row(KeyboardButton(text = _('ℹ Back'))).as_markup()
    )


@router.message(SmsTrans.text)
async def get_message(message: Message, bot_query: BotQueryController, state: FSMContext):
    transaction = await bot_query.get_transaction((await state.get_data())['transaction_id'])

    if message.text == _('ℹ Back'):
        await state.clear()
        return await send_transaction(message, transaction)

    await bot_query.send_sms_transaction(transaction, message.text)
    # todo send user


@router.callback_query(ControlTransMerch.filter(F.message == 2))
async def history_messages(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                           bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    messages = await bot_query.get_sms_history_transaction(transaction)

    text = ''  # todo text
    await callback_query.message.edit_text(
        text = text_transaction(transaction, merchant = True, desc = _("Messages: "), small = True),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(text = _('ℹ Back'),
                                 callback_data = ControlTransMerch(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransMerch.filter(F.accept == 1))
async def accept(callback_query: CallbackQuery, callback_data: ControlTransMerch, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(transaction, merchant = True, desc = _("Do you want accept transaction?")),
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
async def accept_proof(callback_query: CallbackQuery, callback_data: ControlTransMerch,
                       bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.merchant_get_transaction_money(transaction)
    await get_transaction(callback_query, callback_data, bot_query)


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
