from typing import Optional

from aiogram import Router, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.bot_query import BotQueryController

router = Router()


class AskMessage(CallbackData, prefix = "bids_show"):
    user_id: int
    bid_id: Optional[int] = None


class AskState(StatesGroup):
    message = State()


@router.callback_query(AskMessage.filter())
async def pre_send_ask(query: CallbackQuery, callback_data: AskMessage, state: FSMContext):
    await query.message.answer("Напишите сообщение, которое хотите отправить пользователю")
    await state.set_state(AskState.message)
    await state.update_data(bid_id = callback_data.bid_id)
    await state.update_data(user_id = callback_data.user_id)


@router.message(AskState.message)
async def send_ask(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    data = await state.get_data()
    bid = None
    if data['bid_id']:
        bid = await bot_query.get_bid(data['bid_id'])

    await message.answer(f"Сообщение отправлено пользователю")

    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text = f"Ответить", callback_data = AskMessage(
        user_id = bot_query.get_user().id,
    ).pack()))

    if bid:
        await bot.send_message(chat_id = data['user_id'], text = f'Пользователь @{bot_query.get_user().username} '
                                                                 f'написал вам по заявке {bid.id}'
                                                                 f'\n\n{message.text}',
                               reply_markup = keyboard.as_markup())
    else:
        await bot.send_message(chat_id = data['user_id'], text = f'Пользователь @{bot_query.get_user().username} '
                                                                 f'написал вам'
                                                                 f'\n\n{message.text}',
                               reply_markup = keyboard.as_markup())
