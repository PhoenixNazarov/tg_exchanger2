from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot import info
from bot.info import _  # todo delete
from bot.database import Currency, TransGet


router = Router()


def correct_number(number: str):
    try:
        number = float(number.replace(',', '.'))
        if number <= 0:
            out = False
        else:
            out = number * 100 == int(number * 100) or number * 10 == int(number * 10)
    except ValueError:
        out = False
    return out


def correct_phone(number: str):
    number = number.removeprefix('+')
    try:
        out = int(number)

        if out < 0 or (out // (10 ** 9)) == 0:
            out = False
        else:
            out = True

    except ValueError:
        out = False
    return out


class TransactionForm(StatesGroup):
    have_currency = State()
    get_currency = State()
    amount = State()
    rate = State()

    type_get_thb = State()

    cash_town = State()
    cash_region = State()

    bank_bank = State()
    bank_number = State()
    bank_name = State()


@router.message(Command(commands = ['newtrans']))
async def have_currency(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.have_currency)

    builder = ReplyKeyboardBuilder().add(*[KeyboardButton(text = i) for i in Currency.all()])
    await message.answer(
        text = _('What currency do you want to exchange?'),
        reply_markup = builder.as_markup(resize_keyboard = True)
    )


@router.message(TransactionForm.have_currency, F.text == Currency.BAT)
async def get_currency(message: Message, state: FSMContext):
    await state.update_data(get_currency = Currency.BAT)
    await state.set_state(TransactionForm.get_currency)

    builder = ReplyKeyboardBuilder()
    [builder.add(KeyboardButton(text = i)) for i in Currency.fiat()]
    await message.answer(text = _('What currency would you like to receive?'),
                         reply_markup = builder.as_markup(resize_keyboard = True))


@router.message(TransactionForm.have_currency, F.text.in_(Currency.fiat()))
@router.message(TransactionForm.get_currency, F.text.in_(Currency.fiat()))
async def amount(message: Message, state: FSMContext):
    match await state.get_state():
        case TransactionForm.have_currency:
            await state.update_data(have_currency = message.text)
            await state.update_data(get_currency = Currency.BAT)
        case TransactionForm.get_currency:
            await state.update_data(have_currency = Currency.BAT)
            await state.update_data(get_currency = message.text)
        case _:
            raise ValueError
    await state.set_state(TransactionForm.amount)

    await message.answer(
        text = _('Write the amount of {get_currency} of the currency you want to exchange').format(
            **await state.get_data()),
        reply_markup = ReplyKeyboardRemove())


@router.message(TransactionForm.amount, F.text.func(correct_number))
async def rate(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.rate)
    await state.update_data(amount = float(message.text))
    await message.answer(text = _('Write the desired exchange rate {have_currency} ➡️ {get_currency}').format(
        **await state.get_data()))


@router.message(TransactionForm.rate, F.text.func(correct_number))
async def type_receive_thb(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.type_get_thb)
    await state.update_data(rate = float(message.text))

    if (await state.get_data())['get_currency'] == Currency.BAT:
        return await end(message, state)

    await message.answer(text = _("Select the type of receipt THB"),
                         reply_markup = ReplyKeyboardBuilder().
                         add(KeyboardButton(text = str(TransGet.cash)),
                             KeyboardButton(text = str(TransGet.bank_balance))).
                         add(KeyboardButton(text = str(TransGet.atm_machine))).as_markup(resize_keyboard = True))


@router.message(TransactionForm.type_get_thb, F.text == str(TransGet.atm_machine))
async def atm_end(message: Message, state: FSMContext):
    await state.update_data(type_receive_thb = TransGet.atm_machine)
    return await end(message, state)


@router.message(TransactionForm.type_get_thb, F.text == str(TransGet.bank_balance))
async def bank_bank(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.bank_bank)
    await state.update_data(type_receive_thb = TransGet.bank_balance)

    builder = ReplyKeyboardBuilder()
    await message.answer(text = _('Select receiving bank'),
                         reply_markup = builder.add(
                             *[KeyboardButton(text = i) for i in info.BANKS]).as_markup(resize_keyboard = True)
                         )


@router.message(TransactionForm.bank_bank, F.text.in_(info.BANKS))
async def bank_number(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.bank_number)
    await state.update_data(bank_name = message.text)

    await message.answer(text = _('Write the receipt invoice in the format: 9570147158'),
                         reply_markup = ReplyKeyboardRemove())


@router.message(TransactionForm.bank_number, F.text.func(correct_phone))
async def bank_name(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.bank_name)
    await state.update_data(bank_number = message.text)

    await message.answer(text = _('Write the Initials attached to the card in the format: Denis Mandrikov'),
                         reply_markup = ReplyKeyboardRemove())


@router.message(TransactionForm.bank_name)
async def bank_end(message: Message, state: FSMContext):
    await state.update_data(bank_username = message.text)
    return await end(message, state)


@router.message(TransactionForm.type_get_thb, F.text == str(TransGet.cash))
async def cash_town(message: Message, state: FSMContext):
    await state.set_state(TransactionForm.cash_town)
    await state.update_data(type_receive_thb = TransGet.cash)

    await message.answer(text = _('Choose city'),
                         reply_markup = ReplyKeyboardBuilder().add(
                             *[KeyboardButton(text = i) for i in info.TOWNS]).as_markup(resize_keyboard = True)
                         )


@router.message(TransactionForm.cash_town, F.text.in_(info.TOWNS))
async def cash_region(message: Message, state: FSMContext):
    if await state.get_state() == TransactionForm.cash_town:
        await state.update_data(cash_town = message.text)
        await state.set_state(TransactionForm.cash_region)

    await message.answer(text = _('Choose an area'),
                         reply_markup = ReplyKeyboardBuilder().add(
                             *[KeyboardButton(text = i) for i in info.TOWNS[(await state.get_data())['cash_town']]])
                         .as_markup(resize_keyboard = True)
                         )


@router.message(TransactionForm.cash_region)
async def cash_end(message: Message, state: FSMContext):
    if message.text not in info.TOWNS[(await state.get_data())['cash_town']]:
        return await cash_region(message, state)
    await state.update_data(cash_region = message.text)
    return await end(message, state)


@router.message(TransactionForm.amount)
@router.message(TransactionForm.rate)
async def error_incorrect_number(message: Message):
    await message.answer(text = _(
        "You entered an invalid value.\n\n Valid values: 12, 10.1, 10.11. You also can't use decimal "
        'value, greater than hundredths.'))


async def end(message: Message, state: FSMContext):
    await message.answer(text = _('Application creation completed'),
                         reply_markup = ReplyKeyboardBuilder().add(KeyboardButton(text = _('Public')),
                                                                   KeyboardButton(text = _('Cancel')))
                         .as_markup(resize_keyboard = True))

    return await state.get_data()
