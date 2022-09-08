from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder, \
    ReplyKeyboardBuilder, KeyboardButton

from bot.database.models import Transaction, TransStatus
from bot.handlers.private.users.make_transaction import correct_number
from bot.info import _
from bot.messages.transactions import text_transaction, ControlTransUser, ControlTransMerch
from bot.services.bot_query import BotQueryController

router = Router()


class EditTrans(StatesGroup):
    float_value = State()


class SmsTrans(StatesGroup):
    text = State()


def get_main_keyboard(transaction: Transaction) -> KeyboardBuilder[InlineKeyboardButton]:
    if transaction.status == TransStatus.in_stack:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('⚙️ Edit'),
                callback_data = ControlTransUser(id_transaction = transaction.id, edit = 1).pack()),
            InlineKeyboardButton(
                text = _('❌ Cancel'),
                callback_data = ControlTransUser(id_transaction = transaction.id, cancel = 1).pack())
        )
    elif transaction.status == TransStatus.in_exchange:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Edit'),
                callback_data = ControlTransUser(id_transaction = transaction.id, edit = 1).pack()),
            InlineKeyboardButton(
                text = _('❌ Cancel'),
                callback_data = ControlTransUser(id_transaction = transaction.id, cancel = 1).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTransUser(id_transaction = transaction.id, complain = 1).pack())
        )
    elif transaction.status == TransStatus.wait_good_user:
        return InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('📩 Write a message'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 1).pack()),
            InlineKeyboardButton(
                text = _('✉️ Message history'),
                callback_data = ControlTransUser(id_transaction = transaction.id, message = 2).pack()),
        ).row(
            InlineKeyboardButton(
                text = _('✅ Accept'),
                callback_data = ControlTransUser(id_transaction = transaction.id, cancel = 1).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⛔ Complain'),
                callback_data = ControlTransUser(id_transaction = transaction.id, complain = 1).pack())
        )


async def send_transaction(message: Message, transaction: Transaction):
    return await message.answer(
        text = text_transaction(await transaction.to_json()),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.message(Command(commands = 'mytrans'))
async def get_transactions(message: Message, bot_query: BotQueryController):
    transactions = await bot_query.get_exchange_transactions()
    return [await send_transaction(message, trans) for trans in transactions]


@router.callback_query(ControlTransUser.filter(F.main == 1))
async def get_transaction(callback_query: CallbackQuery, callback_data: ControlTransUser,
                          bot_query: BotQueryController, state: FSMContext):
    if await state.get_state() == EditTrans.float_value:
        await state.clear()

    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json()),
        reply_markup = get_main_keyboard(transaction).as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.edit == 1))
async def edit_list(callback_query: CallbackQuery, callback_data: ControlTransUser,
                    bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), desc = _("What do you want edit?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('⚙️ Amount of give currency'),
                callback_data = ControlTransUser(id_transaction = transaction.id, edit = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Rate'),
                callback_data = ControlTransUser(id_transaction = transaction.id, edit = 3).pack())
        ).row(
            InlineKeyboardButton(
                text = _('⚙️ Amount of receive currency'),
                callback_data = ControlTransUser(id_transaction = transaction.id, edit = 4).pack())
        ).row(
            InlineKeyboardButton(
                text = _('ℹ Back'),
                callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.edit.in_({2, 3, 4})))
async def edit(callback_query: CallbackQuery, callback_data: ControlTransUser, bot_query: BotQueryController,
               state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)
    await state.set_state(EditTrans.float_value)
    await state.update_data(id_transaction = callback_data.id_transaction)

    cancel_keyboard = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text = _('❌ Cancel'),
                             callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack())
    ).as_markup()

    if callback_data.edit == 2:
        await state.update_data(key = 'have_amount')
        await state.set_state(EditTrans.float_value)
        await callback_query.message.edit_text(
            text = text_transaction(await transaction.to_json(), desc = _('Write new value of give amount'),
                                    small = True),
            reply_markup = cancel_keyboard
        )
    elif callback_data.edit == 3:
        await state.update_data(key = 'rate')
        await state.set_state(EditTrans.float_value)
        await callback_query.message.edit_text(
            text = text_transaction(await transaction.to_json(), desc = _('Write new value of rate'), small = True),
            reply_markup = cancel_keyboard
        )
    elif callback_data.edit == 4:
        await state.update_data(key = 'get_amount')
        await state.set_state(EditTrans.float_value)
        await callback_query.message.edit_text(
            text = text_transaction(await transaction.to_json(), desc = _('Write new value of receive amount'),
                                    small = True),
            reply_markup = cancel_keyboard
        )


@router.message(EditTrans.float_value)
async def edit_value(message: Message, bot_query: BotQueryController, state: FSMContext):
    new_value = correct_number(message.text)
    if not new_value:
        return await message.answer(text = _(
            "You entered an invalid value"
            "\n\nValid values: 12, 10.1, 10.11. You also can't use decimal value, greater than hundredths"))

    transaction = await bot_query.get_transaction((await state.get_data())['id_transaction'])
    if message.text == _('❌ Cancel'):
        await state.clear()
        return await send_transaction(message, transaction)

    edit_key = (await state.get_data())['key']
    transaction = await bot_query.change_transaction(transaction, edit_key, new_value)
    await send_transaction(message, transaction)
    # todo notif merchant


@router.callback_query(ControlTransUser.filter(F.cancel == 1))
async def cancel(callback_query: CallbackQuery, callback_data: ControlTransUser,
                 bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), desc = _("Do you want cancel transaction?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('✅ Yes'),
                callback_data = ControlTransUser(id_transaction = transaction.id, cancel = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('❌ No'),
                callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.cancel == 2))
async def cancel_proof(callback_query: CallbackQuery, callback_data: ControlTransUser,
                       bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await bot_query.user_cancel_transaction(transaction)
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), desc = _("You cancelled this transaction")),
        reply_markup = InlineKeyboardBuilder().as_markup()
    )
    # todo notif merchant


@router.callback_query(ControlTransUser.filter(F.message == 1))
async def write_message(callback_query: CallbackQuery, callback_data: ControlTransUser, bot_query: BotQueryController,
                        state: FSMContext):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await state.set_state(SmsTrans.text)
    await state.update_data(id_transaction = callback_data.id_transaction)
    await callback_query.message.delete()
    await callback_query.message.answer(
        text = text_transaction(await transaction.to_json(), desc = _("Write your messages"), small = True),
        reply_markup = ReplyKeyboardBuilder().row(KeyboardButton(text = _('ℹ Back'))).as_markup(resize_keyboard = True)
    )


@router.message(SmsTrans.text)
async def get_message(message: Message, bot_query: BotQueryController, state: FSMContext, bot: Bot):
    transaction = await bot_query.get_transaction((await state.get_data())['id_transaction'])

    if message.text == _('ℹ Back'):
        await state.clear()
        return await send_transaction(message, transaction)

    message = await bot_query.send_sms_transaction(transaction, message.text)
    await bot.send_message(
        chat_id = transaction.merchant_id,
        text = text_transaction(await transaction.to_json(), merchant = True,
                                desc = _('New message\n {text}').format(text = message.text), small = True),
        reply_markup = InlineKeyboardBuilder()
        .row(
            InlineKeyboardButton(text = '✉️ Answer',
                                 callback_data = ControlTransMerch(id_transaction = transaction.id, message = 1).pack()))
        .row(
            InlineKeyboardButton(text = 'ℹ Transaction',
                                 callback_data = ControlTransMerch(id_transaction = transaction.id, main = 1).pack()))
        .as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.message == 2))
async def history_messages(callback_query: CallbackQuery, callback_data: ControlTransUser,
                           bot_query: BotQueryController):
    transaction: Transaction = await bot_query.get_transaction(callback_data.id_transaction)
    messages = await bot_query.get_sms_history_transaction(transaction)

    text = '\n'.join(
        [_('Merchant: {text}').format(text = i.text) if i.from_merchant else _('Maker: {text}').format(text = i.text)
         for i in messages])
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(),
                                desc = _("Message history:\n{messages}").format(messages = text),
                                small = True),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(text = _('ℹ Back'),
                                 callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.accept == 1))
async def accept(callback_query: CallbackQuery, callback_data: ControlTransUser, bot_query: BotQueryController):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json(), desc = _("Do you want accept transaction?")),
        reply_markup = InlineKeyboardBuilder().row(
            InlineKeyboardButton(
                text = _('✅ Yes'),
                callback_data = ControlTransUser(id_transaction = transaction.id, accept = 2).pack())
        ).row(
            InlineKeyboardButton(
                text = _('❌ No'),
                callback_data = ControlTransUser(id_transaction = transaction.id, main = 1).pack())
        ).as_markup()
    )


@router.callback_query(ControlTransUser.filter(F.accept == 2))
async def accept_proof(callback_query: CallbackQuery, callback_data: ControlTransUser, bot_query: BotQueryController,
                       bot: Bot):
    transaction = await bot_query.get_transaction(callback_data.id_transaction)

    transaction = await bot_query.user_get_transaction_money(transaction)
    await callback_query.message.edit_text(
        text = text_transaction(await transaction.to_json()),
        reply_markup = InlineKeyboardBuilder().as_markup()
    )

    await bot.send_message(
        chat_id = transaction.merchant_id,
        text = text_transaction(await transaction.to_json(), merchant = True,
                                desc = _('User accept transaction'))
    )

    return 'finish'


@router.callback_query(ControlTransUser.filter(F.complain == 1))
async def complain_list(callback_query: CallbackQuery, callback_data: ControlTransUser,
                        bot_query: BotQueryController):
    # todo
    return
    #
    # transaction = await bot_query.get_transaction(callback_data.id_transaction)
    #
    # await bot_query.user_get_transaction_money(transaction)
    # await get_transaction(callback_query, callback_data, bot_query)
