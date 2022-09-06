from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder, \
    ReplyKeyboardBuilder, KeyboardButton

from bot.database.models import Transaction, TransStatus
from bot.handlers.private.users.make_transaction import correct_number
from bot.info import _
from bot.messages.transactions import text_transaction
from bot.services.bot_query import BotQueryController

router = Router()


class ControlTrans(CallbackData, prefix = "my_trans_user"):
    id_transaction: int

    main: int = 0

    cancel: int = 0  # 1-proof, 2-complain
    edit: int = 0  # 1-list edits, 2-have_amount, 3-rate, 4-get_amount

    message: int = 0  # 1-write, 2-history
    accept: int = 0  # 1-proof, 2-accept

    complain: int = 0  # 1-proof, 2-complain


class EditTrans(StatesGroup):
    float_value = State()


class SmsTrans(StatesGroup):
    text = State()


def get_main_keyboard(transaction: Transaction) -> KeyboardBuilder[InlineKeyboardButton]:
    if transaction.status == TransStatus.in_stack:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('⚙️ Edit'),
                callback_data = ControlTrans(id_transaction = transaction.id, edit = 1).pack()),
            InlineKeyboardButton(
                text = _('❌ Cancel'),
                callback_data = ControlTrans(id_transaction = transaction.id, cancel = 1).pack())
        )
    elif transaction.status == TransStatus.in_exchange:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTrans(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTrans(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Edit'),
                callback_data = ControlTrans(id_transaction = transaction.id, edit = 1).pack()),
            InlineKeyboardButton(
                text = _('❌ Cancel'),
                callback_data = ControlTrans(id_transaction = transaction.id, cancel = 1).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTrans(id_transaction = transaction.id, complain = 1).pack())
        )
    elif transaction.status == TransStatus.wait_good_user:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTrans(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTrans(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('✅ Accept'),
                callback_data = ControlTrans(id_transaction = transaction.id, cancel = 1).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTrans(id_transaction = transaction.id, complain = 1).pack())
        )


async def send_transaction(message: Message, transaction: Transaction):
    await message.answer(
        text = text_transaction(transaction),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.message(Command(commands = '/mytrans'))
async def get_transactions(message: Message, bot_query: BotQueryController):
    transactions = await bot_query.get_exchange_transactions()
    for trans in transactions:
        await send_transaction(message, trans)


@router.callback_query(ControlTrans.filter(F.main == 1))
async def get_transaction(callback_query: CallbackQuery, callback_data: ControlTrans, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(transaction),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.callback_query(ControlTrans.filter(F.edit == 1))
async def edit_list(callback_query: CallbackQuery, callback_data: ControlTrans,
                    bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("What do you want edit?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('⚙️ Amount of give currency'),
                callback_data = ControlTrans(id_transaction = transaction.id, edit = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Rate'),
                callback_data = ControlTrans(id_transaction = transaction.id, edit = 3).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Amount of receive currency'),
                callback_data = ControlTrans(id_transaction = transaction.id, edit = 4).pack())
        ).row(
            InlineKeyboardButton(
                text = _('ℹ Back'),
                callback_data = ControlTrans(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTrans.filter(F.edit.in_({2, 3, 4})))
async def edit(callback_query: CallbackQuery, callback_data: ControlTrans, bot_query: BotQueryController,
               state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await state.set_state(EditTrans.float_value)
    await state.update_data(id_transaction = callback_data.id_transaction)

    cancel_keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text = _('❌ Cancel'))
    ).as_markup()

    if ControlTrans.edit == 2:
        await state.update_data(key = 'have_amount')
        await callback_query.message.edit_text(
            text = text_transaction(transaction, desc = _('Write new value of give amount'), small = True),
            reply_markup = cancel_keyboard
        )
    elif ControlTrans.edit == 3:
        await state.update_data(key = 'rate')
        await callback_query.message.edit_text(
            text = text_transaction(transaction, desc = _('Write new value of rate'), small = True),
            reply_markup = cancel_keyboard
        )
    elif ControlTrans.edit == 4:
        await state.update_data(key = 'get_amount')
        await callback_query.message.edit_text(
            text = text_transaction(transaction, desc = _('Write new value of receive amount'), small = True),
            reply_markup = cancel_keyboard
        )


@router.message(EditTrans.float_value)
async def edit_value(message: Message, bot_query: BotQueryController, state: FSMContext):
    new_value = correct_number(message.text)
    if not new_value:
        return await message.answer(text = _(
            "You entered an invalid value"
            "\n\nValid values: 12, 10.1, 10.11. You also can't use decimal value, greater than hundredths"))

    transaction = await bot_query.get_transaction((await state.get_data())['transaction_id'])
    if message.text == _('❌ Cancel'):
        await state.clear()
        return await send_transaction(message, transaction)

    edit_key = (await state.get_data())['key']
    transaction = await bot_query.change_transaction(transaction, edit_key, new_value)
    await send_transaction(message, transaction)


@router.callback_query(ControlTrans.filter(F.cancel == 1))
async def cancel(callback_query: CallbackQuery, callback_data: ControlTrans,
                 bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("Do you want cancel transaction?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('✅ Yes'),
                callback_data = ControlTrans(id_transaction = transaction.id, cancel = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('❌ No'),
                callback_data = ControlTrans(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTrans.filter(F.cancel == 2))
async def cancel_proof(callback_query: CallbackQuery, callback_data: ControlTrans,
                       bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.user_cancel_transaction(transaction)
    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("You cancelled this transaction")),
        reply_markup = InlineKeyboardBuilder().as_markup()
    )


@router.callback_query(ControlTrans.filter(F.message == 1))
async def write_message(callback_query: CallbackQuery, callback_data: ControlTrans, bot_query: BotQueryController,
                        state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.user_cancel_transaction(transaction)
    await state.set_state(SmsTrans.text)
    await state.update_data(id_transaction = callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("Write your messages"), small = True),
        reply_markup = ReplyKeyboardBuilder().row(KeyboardButton(text = _('ℹ Back'))).as_markup()
    )


@router.message(SmsTrans.text)
async def get_message(message: Message, bot_query: BotQueryController, state: FSMContext):
    transaction = await bot_query.get_transaction((await state.get_data())['transaction_id'])

    if message.text == _('ℹ Back'):
        await state.clear()
        return await send_transaction(message, transaction)

    await bot_query.send_sms_transaction(transaction, message.text)
    # todo send merchant


@router.callback_query(ControlTrans.filter(F.message == 2))
async def history_messages(callback_query: CallbackQuery, callback_data: ControlTrans, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    messages = await bot_query.get_sms_history_transaction(transaction)

    text = ''  # todo text
    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("Messages: "), small = True),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(text = _('ℹ Back'),
                                 callback_data = ControlTrans(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTrans.filter(F.accept == 1))
async def accept(callback_query: CallbackQuery, callback_data: ControlTrans, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(transaction, desc = _("Do you want accept transaction?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('✅ Yes'),
                callback_data = ControlTrans(id_transaction = transaction.id, accept = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('❌ No'),
                callback_data = ControlTrans(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTrans.filter(F.accept == 2))
async def accept_proof(callback_query: CallbackQuery, callback_data: ControlTrans,
                       bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.user_get_transaction_money(transaction)
    await get_transaction(callback_query, callback_data, bot_query)


@router.callback_query(ControlTrans.filter(F.complain == 1))
async def complain_list(callback_query: CallbackQuery, callback_data: ControlTrans,
                        bot_query: BotQueryController):
    # todo
    return
    #
    # transaction = await bot_query.get_transaction(callback_data.id_transaction)
    #
    # await bot_query.user_get_transaction_money(transaction)
    # await get_transaction(callback_query, callback_data, bot_query)
