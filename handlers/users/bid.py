from decimal import Decimal

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database.enums import Currency
from services.bot_query import BotQueryController
from ..free_messages import AskMessage
from ..request import RequestNotification

router = Router()


class BidsCallback(CallbackData, prefix = "bids_show"):
    main: bool
    currency_in: Currency
    currency_out: Currency
    bid_id: int


class BidsAction(CallbackData, prefix = "bids_action"):
    bid_id: int
    accept: bool = False
    message: bool = False


class ChoiceState(StatesGroup):
    amount = State()
    requisites = State()
    request = State()


def get_main_screen(bids):
    keyboard = InlineKeyboardBuilder()

    count = lambda _in, _out: [1 if i.currency_in == _in and i.currency_out == _out else 0 for i in bids].count(1)

    for i in Currency.all():
        for j in Currency.all():
            if i != j and (i == Currency.THB or j == Currency.THB):
                keyboard.row(InlineKeyboardButton(text = f"{i} ➡️ {j} ({count(i, j)})", callback_data = BidsCallback(
                    main = False,
                    currency_in = i,
                    currency_out = j,
                    bid_id = -1
                ).pack()))

    return "Выберите нужную пару", keyboard


@router.message(Command(commands = ['show']))
async def show_bids(message: Message, bot_query: BotQueryController):
    bids = await bot_query.get_bids()
    text, keyboard = get_main_screen(bids)

    await message.answer(
        text = text,
        reply_markup = keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.main == True))
async def show_bids_main(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bids = await bot_query.get_bids()
    text, keyboard = get_main_screen(bids)

    await query.message.edit_text(
        text = text,
        reply_markup = keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.bid_id == -1))
async def show_current_bid_pair(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bids = await bot_query.get_bids()

    keyboard = InlineKeyboardBuilder()

    for i in bids:
        if i.currency_in == callback_data.currency_in and i.currency_out == callback_data.currency_out:
            keyboard.row(InlineKeyboardButton(
                text = f"~{i.rate} {int(i.min_amount)}...{int(i.max_amount)} {i.merchant.username}",
                callback_data = BidsCallback(
                    main = False,
                    currency_in = callback_data.currency_in,
                    currency_out = callback_data.currency_out,
                    bid_id = i.id
                ).pack()))

    keyboard.row(InlineKeyboardButton(text = f"Назад", callback_data = BidsCallback(
        main = True,
        currency_in = callback_data.currency_in,
        currency_out = callback_data.currency_out,
        bid_id = -1
    ).pack()))

    await query.message.edit_text(
        text = "Выберите нужного продавца"
               f"\n<b>Пара:</b> {callback_data.currency_in} ➡️ {callback_data.currency_out}",
        reply_markup = keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.bid_id != -1))
async def show_current_bid_id(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bid = await bot_query.get_bid(callback_data.bid_id)
    if not bid:
        return await query.answer("Нет такой заявки")

    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text = f"Обменять", callback_data = BidsAction(
        bid_id = bid.id,
        accept = True
    ).pack()))

    keyboard.row(InlineKeyboardButton(text = f"Задать вопрос", callback_data = AskMessage(
        bid_id = bid.id,
        user_id = bid.merchant.id
    ).pack()))

    keyboard.row(InlineKeyboardButton(text = f"Назад", callback_data = BidsCallback(
        main = False,
        currency_in = callback_data.currency_in,
        currency_out = callback_data.currency_out,
        bid_id = -1
    ).pack()))

    if bid.currency_in == Currency.USDC:
        currency_m = Currency.USDC
    elif bid.currency_in == Currency.USDT:
        currency_m = Currency.USDT

    elif bid.currency_out == Currency.USDC:
        currency_m = Currency.USDC
    elif bid.currency_out == Currency.USDT:
        currency_m = Currency.USDT

    elif bid.currency_in == Currency.THB:
        currency_m = Currency.THB
    elif bid.currency_out == Currency.THB:
        currency_m = Currency.THB
    else:
        currency_m = Currency.THB

    text = f"<b>Предложение</b>" \
           f"\n\n<b><u>Marchant:</u></b> @{bid.merchant.username} предлагает обменять {bid.currency_in}/{bid.currency_out} по курсу {bid.rate}" \
           f"\n\nMerchant: @{bid.merchant.username} провёл успешных сделок: 0" \
           f"\n\n<b>Депозит:</b>{bid.max_amount} {currency_m}" \
           f"\nРейтинг: (0) 👍 / (0) 👎" \
           f"\n\n{bid.description}" \
           f"\n\n<b><i><u>После принятия условий предложение действует в течении 5 минут.</u></i></b>"

    await query.message.edit_text(
        text = text,
        reply_markup = keyboard.as_markup()
    )


@router.callback_query(BidsAction.filter(F.accept == 1))
async def choice_current_bid_id(query: CallbackQuery, callback_data: BidsAction, state: FSMContext):
    await state.set_state(ChoiceState.amount)
    await state.update_data(bid_id = callback_data.bid_id)
    await query.message.edit_text(
        text = "Напишите желаемую сумму обмена, по умалчанию берётся главная валюта. Если вы хотите указать конкретную валюту, то допишите USD, RUB, THB ... В любое место."
    )


@router.message(ChoiceState.amount)
async def write_amount(message: Message, bot_query: BotQueryController, state: FSMContext):
    bid = await bot_query.get_bid((await state.get_data())["bid_id"])

    _in = bid.currency_in
    _out = bid.currency_out

    # normalize
    text = message.text.lower()
    _currency = None
    normal = {
        'thb': Currency.THB,
        'usdt': Currency.USDT,
        'usdc': Currency.USDC,
        'rub': Currency.RUB
    }
    for k, v in normal.items():
        if k in text:
            _currency = v
            text = text.replace(k, '')
            break
    else:
        if 'usd' in text:
            text = text.replace('usd', '')
            if _in == Currency.USDT or _out == Currency.USDT:
                _currency = Currency.USDT
            elif _in == Currency.USDC or _out == Currency.USDC:
                _currency = Currency.USDC

    if not _currency:
        if _in == Currency.USDT or _out == Currency.USDT:
            _currency = Currency.USDT
        elif _in == Currency.USDC or _out == Currency.USDC:
            _currency = Currency.USDC
        else:
            _currency = Currency.THB

    text = text.replace(' ', '').replace(',', '.')
    print(text)
    amount = Decimal(text)
    try:
        rate = Decimal(bid.rate)
    except:
        return await message.answer("Неверный ввод, Правильный формат: 1000, 1000 THB, USD 1000")

    amount_in = 0
    amount_out = 0
    amount_m = 0
    match _in, _out, _currency:
        case (Currency.THB, Currency.RUB, Currency.THB):
            amount_m = amount_in = amount
            amount_out = amount * rate
        case (Currency.THB, Currency.RUB, Currency.RUB):
            amount_m = amount_in = amount * rate
            amount_out = amount

        case (Currency.RUB, Currency.THB, Currency.RUB):
            amount_in = amount
            amount_m = amount_out = amount / rate
        case (Currency.RUB, Currency.THB, Currency.THB):
            amount_in = amount * rate
            amount_m = amount_out = amount

        case (Currency.USDT | Currency.USDC, Currency.THB, Currency.USDT | Currency.USDC):
            amount_m = amount_in = amount
            amount_out = amount * rate
        case (Currency.USDT | Currency.USDC, Currency.THB, Currency.THB):
            amount_m = amount_in = amount / rate
            amount_out = amount

        case (Currency.THB, Currency.USDT | Currency.USDC, Currency.USDT | Currency.USDC):
            amount_in = amount * rate
            amount_m = amount_out = amount
        case (Currency.THB, Currency.USDT | Currency.USDC, Currency.THB):
            amount_in = amount
            amount_m = amount_out = amount / rate

    # if _in == Currency.USDC or _in == Currency.USDT:
    #     amount_m = amount_in
    # elif _out == Currency.USDC or _out == Currency.USDT:
    #     amount_m = amount_out
    # elif _in == Currency.THB:
    #     amount_m = amount_in
    # elif _out == Currency.THB:
    #     amount_m = amount_out
    # else:
    #     amount_m = amount_out
    if amount_m > bid.max_amount or amount_m < bid.min_amount:
        return await message.answer("Неверный лимит "
                                    f"\n\nМинимум: {bid.min_amount}"
                                    f"\nМаксимум: {bid.max_amount}"
                                    f"\nВы ввели: {round(amount_m, 2)}")

    await state.set_state(ChoiceState.requisites)
    await state.update_data(amount_in = round(amount_in, 2))
    await state.update_data(amount_out = round(amount_out, 2))

    await message.answer(
        text = "Напишите реквизиты, куда хотите получить платеж"
    )


@router.message(ChoiceState.requisites)
async def write_requisites(message: Message, bot_query: BotQueryController, state: FSMContext):
    await state.set_state(ChoiceState.request)
    await state.update_data(requisites = message.text)
    data = await state.get_data()
    bid = await bot_query.get_bid(data["bid_id"])

    keyboard = ReplyKeyboardBuilder().row(KeyboardButton(text = 'Да'), KeyboardButton(text = 'Нет'))

    await message.answer(
        text = "Создать заявку?"
               f"\n<b>Курс:</b> ~{bid.rate}"
               f"\n<b>Отдаёте:</b> {data['amount_in']} {bid.currency_in}"
               f"\n<b>Получаете:</b> {data['amount_out']} {bid.currency_out}"
               f"\n{message.text}"
               f"\n\n<b><i>После принятия условий предложение действует в течении 5 минут.</i></b>",
        reply_markup = keyboard.as_markup(resize_keyboard = True)
    )


@router.message(ChoiceState.request)
async def send_request(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        request = await bot_query.create_request(data['bid_id'], data['requisites'], data['amount_in'],
                                                 data['amount_out'])
        request = await bot_query.get_request(request.id)
        await message.answer(text = 'Вы подтвердили', reply_markup = ReplyKeyboardRemove())
        await RequestNotification(request, bot_query.get_user(), bot).request()
        await state.clear()
    elif message.text == 'Нет':
        await message.answer(text = 'Вы отклонили', reply_markup = ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(text = 'Не понятно')
