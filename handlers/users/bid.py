from aiogram import Router, F, Bot
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database.enums import Currency
from services.bot_query import BotQueryController
from utils.calculate_amount import Calculate, normalize
from .home import home_keyboard
from ..free_messages import AskMessage
from ..request import RequestNotification, RequestActionMerchantRate, RequestActionUserRate

router = Router()


class BidsCallback(CallbackData, prefix="bids_show"):
    main: bool
    currency_in: Currency
    currency_out: Currency
    bid_id: int


class BidsAction(CallbackData, prefix="bids_action"):
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
                keyboard.row(InlineKeyboardButton(text=f"{i} ➡️ {j} ({count(i, j)})", callback_data=BidsCallback(
                    main=False,
                    currency_in=i,
                    currency_out=j,
                    bid_id=-1
                ).pack()))

    return "Выберите нужную пару", keyboard


@router.message(Text(text="💱 Обмен"))
async def show_bids(message: Message, bot_query: BotQueryController):
    bids = await bot_query.get_bids()
    text, keyboard = get_main_screen(bids)

    await message.answer(
        text=text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.main == True))
async def show_bids_main(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bids = await bot_query.get_bids()
    text, keyboard = get_main_screen(bids)

    await query.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.bid_id == -1))
async def show_current_bid_pair(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bids = await bot_query.get_bids()

    keyboard = InlineKeyboardBuilder()

    for i in bids:
        if i.currency_in == callback_data.currency_in and i.currency_out == callback_data.currency_out:
            keyboard.row(InlineKeyboardButton(
                text=f"~{i.rate} {int(i.min_amount)}...{int(i.max_amount)} {i.merchant.username}",
                callback_data=BidsCallback(
                    main=False,
                    currency_in=callback_data.currency_in,
                    currency_out=callback_data.currency_out,
                    bid_id=i.id
                ).pack()))

    keyboard.row(InlineKeyboardButton(text=f"Назад", callback_data=BidsCallback(
        main=True,
        currency_in=callback_data.currency_in,
        currency_out=callback_data.currency_out,
        bid_id=-1
    ).pack()))

    await query.message.edit_text(
        text="Выберите нужного продавца"
             f"\n<b>Пара:</b> {callback_data.currency_in} ➡️ {callback_data.currency_out}",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(BidsCallback.filter(F.bid_id != -1))
async def show_current_bid_id(query: CallbackQuery, callback_data: BidsCallback, bot_query: BotQueryController):
    bid = await bot_query.get_bid(callback_data.bid_id)
    if not bid:
        return await query.answer("Нет такой заявки")

    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text=f"Обменять", callback_data=BidsAction(
        bid_id=bid.id,
        accept=True
    ).pack()))

    keyboard.row(InlineKeyboardButton(text=f"Задать вопрос", callback_data=AskMessage(
        bid_id=bid.id,
        user_id=bid.merchant.id
    ).pack()))

    keyboard.row(InlineKeyboardButton(text=f"Назад", callback_data=BidsCallback(
        main=False,
        currency_in=callback_data.currency_in,
        currency_out=callback_data.currency_out,
        bid_id=-1
    ).pack()))

    currency_m = Calculate(currency_in=bid.currency_in, currency_out=bid.currency_out).get_main_currency()

    text = f"<b>Предложение</b>" \
           f"\n\n<b><u>Marchant:</u></b> @{bid.merchant.username} предлагает обменять {bid.currency_in}/{bid.currency_out} по курсу {bid.rate}" \
           f"\n\nMerchant: @{bid.merchant.username} провёл успешных сделок: 0" \
           f"\n\n<b>Депозит:</b>{bid.max_amount} {currency_m}" \
           f"\nРейтинг: (0) 👍 / (0) 👎" \
           f"\n\n{bid.description}" \
           f"\n\n<b><i><u>После принятия условий предложение действует в течении 5 минут.</u></i></b>"

    await query.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(BidsAction.filter(F.accept == 1))
async def choice_current_bid_id(query: CallbackQuery, callback_data: BidsAction, state: FSMContext):
    await state.set_state(ChoiceState.amount)
    await state.update_data(bid_id=callback_data.bid_id)
    await query.message.edit_text(
        text="Напишите желаемую сумму обмена, по умалчанию берётся главная валюта. Если вы хотите указать конкретную валюту, то допишите USD, RUB, THB ... В любое место."
    )


@router.message(ChoiceState.amount)
async def write_amount(message: Message, bot_query: BotQueryController, state: FSMContext):
    bid = await bot_query.get_bid((await state.get_data())["bid_id"])

    # normalize
    try:
        calc = normalize(message.text, bid.currency_in, bid.currency_out, bid.rate)
    except ValueError:
        return await message.answer("Неверный ввод, Правильный формат: 1000, 1000 THB, USD 1000")

    amount_m = calc.get_main_amount()

    if amount_m > bid.max_amount or amount_m < bid.min_amount:
        return await message.answer("Неверный лимит "
                                    f"\n\nМинимум: {bid.min_amount}"
                                    f"\nМаксимум: {bid.max_amount}"
                                    f"\nВы ввели: {round(amount_m, 2)}")

    if calc.type_in:
        await state.update_data(amount_in=round(calc.amount_in, 2))
    else:
        await state.update_data(amount_out=round(calc.amount_out, 2))

    data = await state.get_data()
    bid = await bot_query.get_bid(data["bid_id"])

    keyboard = ReplyKeyboardBuilder().row(KeyboardButton(text='Да'), KeyboardButton(text='Нет'))

    if data.get('amount_in'):
        text = f"<b>Отдаёте:</b> {data['amount_in']} {bid.currency_in}"
    else:
        text = f"<b>Получаете:</b> {data['amount_out']} {bid.currency_out}"

    await state.set_state(ChoiceState.request)
    await message.answer(
        text="Отправить пользователю запрос на заявку? После вам в ответ прийдет сообщение с курсом."
             f"\n{text}"
             f"\n\n<b><i>После принятия условий предложение действует в течении 5 минут.</i></b>",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.message(ChoiceState.request)
async def send_request(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        bid = await bot_query.get_bid((await state.get_data())["bid_id"])

        if data.get('amount_in'):
            text = f"<b>Отдаёт:</b> {data['amount_in']} {bid.currency_in}"
            amount_ = data['amount_in']
            currency_ = bid.currency_in
        else:
            text = f"<b>Получает:</b> {data['amount_out']} {bid.currency_out}"
            amount_ = data['amount_out']
            currency_ = bid.currency_out

        keyboard = InlineKeyboardBuilder().row(InlineKeyboardButton(text=f"Написать",
                                                                    callback_data=RequestActionMerchantRate(
                                                                        bid_id=bid.id,
                                                                        amount=amount_,
                                                                        currency=currency_,
                                                                        user_id=message.chat.id,
                                                                        accept=1
                                                                    ).pack()),
                                               InlineKeyboardButton(text=f"Отказаться",
                                                                    callback_data=RequestActionMerchantRate(
                                                                        bid_id=bid.id,
                                                                        amount=amount_,
                                                                        currency=currency_,
                                                                        user_id=message.chat.id,
                                                                        cancel=1
                                                                    ).pack())
                                               )

        await message.answer(text='Вы подтвердили', reply_markup=home_keyboard.as_markup(resize_keyboard=True))
        await bot.send_message(chat_id=bid.merchant_id,
                               text=f"Запрос по заявке {bid.id} {bid.currency_in}/{bid.currency_out}"
                                    f"\nПользователь @{message.chat.username}"
                                    f"\n{text}"
                                    "\nНапишите курс",
                               reply_markup=keyboard.as_markup())

        await state.clear()

    elif message.text == 'Нет':
        await message.answer(text='Вы отклонили', reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        pass


@router.callback_query(RequestActionUserRate.filter(F.cancel == 1))
async def accept(query: CallbackQuery, callback_data: RequestActionUserRate, state: FSMContext):
    await query.message.delete()


@router.callback_query(RequestActionUserRate.filter(F.accept == 1))
async def accept(query: CallbackQuery, callback_data: RequestActionUserRate, bot_query: BotQueryController,
                 state: FSMContext):
    bid = await bot_query.get_bid(callback_data.bid_id)

    await state.set_state(ChoiceState.requisites)
    await state.update_data(bid_id=bid.id)
    await state.update_data(amount=callback_data.amount)
    await state.update_data(currency=callback_data.currency)
    await state.update_data(rate=callback_data.rate)

    await query.message.answer(text="Напишите реквизиты, куда хотите получить платеж")


@router.message(ChoiceState.requisites)
async def write_requisites(message: Message, bot_query: BotQueryController, state: FSMContext, bot: Bot):
    data = await state.get_data()
    bid = await bot_query.get_bid(data.get('bid_id'))
    calc = normalize(f"{data.get('amount')} {data.get('currency')}", bid.currency_in, bid.currency_out,
                     data.get('rate'))
    request = await bot_query.create_request(data['bid_id'], message.text, calc.amount_in,
                                             calc.amount_out)
    request = await bot_query.get_request(request.id)
    await message.answer(text='Вы подтвердили', reply_markup=ReplyKeyboardRemove())
    await RequestNotification(request, bot_query.get_user(), bot).request()
    await state.clear()
