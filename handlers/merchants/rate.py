from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.bot_query import BotQueryController
from utils.calculate_amount import Calculate, normalize
from ..request import RequestActionMerchantRate, RequestActionUserRate

router = Router()


class RequestRate(StatesGroup):
    rate = State()


@router.callback_query(RequestActionMerchantRate.filter(F.accept == 1))
async def accept(query: CallbackQuery, callback_data: RequestActionMerchantRate, state: FSMContext):
    await state.set_state(RequestRate.rate)
    await query.message.delete()
    await state.update_data(bid_id = callback_data.bid_id)
    await state.update_data(amount = callback_data.amount)
    await state.update_data(currency = callback_data.currency)
    await state.update_data(user_id = callback_data.user_id)
    await query.message.answer("Напишите курс")


@router.callback_query(RequestActionMerchantRate.filter(F.cancel == 1))
async def accept(query: CallbackQuery, callback_data: RequestActionMerchantRate, state: FSMContext):
    await query.message.delete()


@router.message(RequestRate.rate)
async def send_rate(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    data = await state.get_data()
    bid = await bot_query.get_bid((await state.get_data())["bid_id"])

    rate = message.text
    try:
        rate = float(rate.replace(',', '.'))
    except:
        await message.answer(text = 'Неверный формат курса')
        return

    keyboard = InlineKeyboardBuilder().row(InlineKeyboardButton(text = f"Принять",
                                                                callback_data = RequestActionUserRate(
                                                                    bid_id = bid.id,
                                                                    amount = data.get('amount'),
                                                                    currency = data.get('currency'),
                                                                    rate = rate,
                                                                    accept = 1
                                                                ).pack()),
                                           InlineKeyboardButton(text = f"Отказаться",
                                                                callback_data = RequestActionUserRate(
                                                                    bid_id = bid.id,
                                                                    amount = data.get('amount'),
                                                                    currency = data.get('currency'),
                                                                    rate = rate,
                                                                    cancel = 1
                                                                ).pack()),
                                           )

    calc = normalize(f"{data.get('amount')} {data.get('currency')}", bid.currency_in, bid.currency_out, rate)

    await message.answer(text = 'Сообщение отправлено пользователю')
    await bot.send_message(chat_id = data.get('user_id'),
                           text = "Создать заявку?"
                                  f"\n<b>Курс:</b> {rate}"
                                  f"\n<b>Отдаёте:</b> {calc.amount_in} {bid.currency_in}"
                                  f"\n<b>Получаете:</b> {calc.amount_out} {bid.currency_out}",
                           reply_markup = keyboard.as_markup())

    await state.clear()
