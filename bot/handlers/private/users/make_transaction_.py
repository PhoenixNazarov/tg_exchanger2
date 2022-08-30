from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.config_reader import config
from bot.database import Currency, TransGet


def _(a): return a


router = Router()


def incorrect_number(number: str):
    try:
        number = float(number.replace(',', '.'))
        out = number * 100 == int(number * 100)
    except ValueError:
        out = False
    return not out


def incorrect_phone(number: str):
    if len(number) != 9:
        return True
    try:
        out = int(number)
    except ValueError:
        out = False
    return not out


class FSMTransaction(StatesGroup):
    have_currency = State()
    get_currency = State()
    amount = State()
    rate = State()

    type_get_thb = State()


class FSMTransactionShort(StatesGroup):
    get_currency = State()
    amount = State()
    rate = State()


class FSMCash(StatesGroup):
    town = State()
    region = State()


class FSMBank(StatesGroup):
    bank = State()
    number = State()
    name = State()


@router.message(commands = ['newtrans'])
@router.message(state = FSMTransaction.have_currency)
async def have_currency(message: Message, state: FSMContext):
    await state.set_state(FSMTransaction.have_currency)
    builder = ReplyKeyboardBuilder()
    [builder.add(KeyboardButton(text = i)) for i in Currency.all()]
    await message.answer(
        text = _('What currency do you want to exchange?'),
        reply_markup = builder.as_markup(resize_keyboard = True)
    )


async def get_currency(message: Message, state: FSMContext):
    await state.set_state(FSMTransaction.have_currency)
    builder = ReplyKeyboardBuilder()
    [builder.add(KeyboardButton(text = i)) for i in Currency.all()]
    await message.answer(
        text = _('What currency do you want to exchange?'),
        reply_markup = builder.as_markup(resize_keyboard = True)
    )


# Base settings of transaction
@router.message(F.text == Currency.BAT, state = FSMTransaction.have_currency)
async def load_have_currency_1(message: Message, state: FSMContext):
    await state.update_data({'have_currency': Currency.BAT})
    await load_get_currency_inv(message, state)
    await state.set_state(FSMTransactionShort.get_currency)


@router.message(F.text.in_(Currency.fiat()), state = FSMTransaction.have_currency)
async def load_have_currency_1(message: Message, state: FSMContext):
    await state.update_data({'have_currency': message.text, 'get_currency': Currency.BAT})
    await message.answer(**make_transaction_amount(message.text))
    await state.set_state(FSMTransaction.amount)


# because fiat only Bat


@router.message(F.text.in_(Currency.fiat()), state = FSMTransactionShort.get_currency)
async def load_get_currency_inv(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    [builder.add(KeyboardButton(text = i)) for i in Currency.fiat()]
    await message.answer(text = _('What currency would you like to receive?'),
                         reply_markup = builder.as_markup(resize_keyboard = True))


@router.message(state = FSMTransactionShort.get_currency)
async def load_get_currency(message: Message, state: FSMContext):
    await state.update_data({'get_currency': message.text})
    await message.answer(
        text = _('Write the amount of {currency} of the currency you want to exchange').format(
            currency = message.text),
        reply_markup = ReplyKeyboardRemove())
    await state.set_state(FSMTransaction.amount)


@router.message(F.text.func(incorrect_number),
                state = [FSMTransaction.amount, FSMTransaction.rate,
                         FSMTransactionShort.amount, FSMTransactionShort.rate])
async def error_incorrect_number(message: Message):
    await message.answer(text = _(
        "You entered an invalid value.\n\n Valid values: 12, 10.1, 10.11. You also can't use decimal "
        'value, greater than hundredths.'))


@router.message(state = [FSMTransaction.amount, FSMTransactionShort.amount])
async def load_amount(message: Message, state: FSMContext):
    await state.update_data({'amount': float(message.text.replace(',', '.'))})
    await message.answer(text = _('Write the desired exchange rate {have_currency} ➡️ {get_currency}').format(
        **await state.get_data()))
    await state.set_state(FSMTransaction.rate)


@router.message(state = FSMTransactionShort.rate)
async def load_rate_short(message: Message, state: FSMContext, session):
    await state.update_data({'rate': float(message.text.replace(',', '.')), 'type_get_thb': TransGet.none})
    await send_pre_transaction(message, await state.get_data(), session)


@router.message(state = FSMTransaction.rate)
async def load_rate(message: Message, state: FSMContext, session):
    await state.update_data({'rate': float(message.text.replace(',', '.'))})
    await show_receipt_thb(message)
    await state.set_state(FSMTransaction.type_get_thb)


# Type get thb
async def show_receipt_thb(message: Message):
    builder = ReplyKeyboardBuilder()

    await message.answer(text = _("Select the type of receipt THB"),
                         reply_markup = builder.add(KeyboardButton(text = str(TransGet.cash)),
                                                    KeyboardButton(text = str(TransGet.bank_balance))).add(
                             KeyboardButton(text = str(TransGet.atm_machine))).as_markup(resize_keyboard = True))


@router.message(F.text == TransGet.atm_machine, state = FSMTransaction.type_get_thb)
async def load_type_get_thb_2(message: Message, state: FSMContext, session):
    await build_transaction(message, state, session)

    # todo in
@router.message(not F.text.in_(TransGet), state = FSMTransaction.type_get_thb)
async def load_type_get_thb_1(message: Message):
    await show_receipt_thb(message)


# Type get thb CASH
@router.message(F.text == TransGet.cash, state = FSMTransaction.type_get_thb)
@router.message(lambda message: message.text not in config.TOWNS, state = FSMCash.town)
async def show_town(message: Message, state):
    await state.set_state(FSMCash.town)
    await message.answer(text = _('Choose city'),
                         reply_markup =
                         ReplyKeyboardMarkup(resize_keyboard = True).add(
                             *[KeyboardButton(i) for i in config.TOWNS.keys()])
                         )


@router.message(state = FSMCash.town)
async def load_town(message: Message, state: FSMContext):
    await state.update_data(town = message.text)
    await show_region(message, state)
    await state.set_state(FSMCash.region)


async def show_region(message: Message, state: FSMContext):
    await message.answer(text = _('Choose an area'),
                         reply_markup =
                         ReplyKeyboardMarkup(resize_keyboard = True).add(
                             *[KeyboardButton(i) for i in config.TOWNS[state.get_data('town')]]))


@router.message(state = FSMCash.region)
async def load_region(message: Message, state: FSMContext, session):
    async with state.proxy() as data:
        if message.text not in config.TOWNS[data['town']]:
            return await show_region(message, state)

        data['region'] = message.text
        await build_transaction(message, state, session)


# Type get thb BANK
@router.message(F.text == TransGet.bank_balance, state = FSMTransaction.type_get_thb)
@router.message(lambda message: message.text not in config.BANKS, state = FSMBank.bank)
async def show_bank(message: Message, state: FSMContext):
    await state.set_state(FSMBank.bank)
    await message.answer(text = _('Select receiving bank'),
                         reply_markup = ReplyKeyboardMarkup(resize_keyboard = True).add(
                             *[KeyboardButton(i) for i in config.BANKS])
                         )


@router.message(state = FSMBank.bank)
async def load_bank(message: Message, state: FSMContext):
    await state.update_data(bank = message.text)
    await show_trans_number(message)
    await FSMBank.next()


@router.message(lambda message: correct_phone(message.text), state = FSMBank.number)
async def show_trans_number(message: Message):
    await message.answer(text = _('Write the receipt invoice in the format: 9570147158'),
                         reply_markup = ReplyKeyboardRemove())


@router.message(state = FSMBank.number)
async def load_number(message: Message, state: FSMContext):
    await state.update_data(number = int(message.text))
    await message.answer(text = _('Write the Initials attached to the card in the format: Denis Mandrikov'),
                         reply_markup = ReplyKeyboardRemove())
    await FSMBank.next()


@router.message(state = FSMBank.name)
async def load_name(message: Message, state: FSMContext, session):
    await state.update_data(name = message.text)
    await build_transaction(message, state, session)


# End make transaction
async def build_transaction(message: Message, state: FSMContext, session):
    await message.answer(text = _('Application creation completed'),
                         reply_markup = ReplyKeyboardRemove())
    with state.proxy() as data:
        await send_pre_transaction(message, dict(data), session)
    await state.finish()


async def send_pre_transaction(message: Message, callback_data, session):
    transaction = await create_pre_transaction(session, callback_data, message.conf['user'])
    await message.answer(text = _('{transaction_user_description}'
                                  '\n{transaction_receive_description}').format(
        transaction_user_description = get_trans_description_user(transaction),
        transaction_receive_description = get_transaction_type_thb_detail(transaction, True),
        transaction = transaction),
        reply_markup = InlineKeyboardMarkup().row(
            InlineKeyboardButton(RepeatingText.publish,
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 1)),
            InlineKeyboardButton(RepeatingText.cancel,
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 0))))


@router.callback_query_handler(make_transaction_cd.filter(public = '1'), state = '*')
async def public_transaction(query: CallbackQuery, callback_data: dict, session):
    transaction = await public_transaction_db(session, await get_transaction_moderate(session, callback_data['id']))

    await bot.edit_message_text(**get_transaction_user(transaction), chat_id = query.message.chat.id,
                                message_id = query.message.message_id)

    merchant_message = await bot.send_message(chat_id = config.MERCHANT_CHANNEL,
                                              **get_transaction_channel(transaction))

    await transaction_set_merchant_message(session, transaction, merchant_message.message_id)


@router.callback_query_handler(make_transaction_cd.filter(), state = '*')
async def delete_pre_transaction(query: CallbackQuery, callback_data: dict, session):
    await bot.delete_message(chat_id = query.from_user.id, message_id = query.message.message_id)
    await un_public_transaction(session, await get_transaction_moderate(session, callback_data['id']))

