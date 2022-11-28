from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.enums import RequestStatus
from database.models import MessageSender
from services.bot_query import BotQueryController
from ..request import RequestNotification, RequestActionMerchant

router = Router()


class RequestRequisites(StatesGroup):
    requisites = State()


class RequestMessage(StatesGroup):
    text = State()


@router.message(Command(commands = 'requests_merchant'))
async def show_requests(message: Message, bot_query: BotQueryController, bot: Bot):
    requests = await bot_query.get_my_requests(True)
    for i in requests:
        await RequestNotification(i, bot_query.get_user(), bot).send_merchant_request()


# STATUS
@router.callback_query(RequestActionMerchant.filter(F.request.is_not(None)))
async def request_merchant(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                           bot: Bot):
    request = await bot_query.get_request(callback_data.request_id)
    await query.message.delete()

    if not callback_data.request:
        await bot_query.change_status(callback_data.request_id, RequestStatus.request_merchant)
        await RequestNotification(request, bot_query.get_user(), bot).cancel()
    else:
        await bot_query.change_status(callback_data.request_id, RequestStatus.request_merchant)
        await RequestNotification(request, bot_query.get_user(), bot).request()


@router.callback_query(RequestActionMerchant.filter(F.requisites == 1))
async def pre_send_requisites(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                              state: FSMContext):
    await state.set_state(RequestRequisites.requisites)
    await state.update_data(request_id = callback_data.request_id)
    await query.message.answer("Введите реквизиты для принятия перевода.")


@router.message(RequestRequisites.requisites)
async def send_requisites(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    requisites = message.text
    await bot_query.set_merchant_requisites((await state.get_data())['request_id'], requisites)
    await bot_query.change_status((await state.get_data())['request_id'], RequestStatus.requisites_merchant)
    request = await bot_query.get_request((await state.get_data())['request_id'])
    await RequestNotification(request, bot_query.get_user(), bot).send_requisites()


@router.callback_query(RequestActionMerchant.filter(F.accept == 1))
async def pre_accept(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                     bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text = f"Да", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            accept = 2
        ).pack()),
        InlineKeyboardButton(text = f"Нет", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            main = 1
        ).pack())
    )
    await query.message.edit_text(text = 'Вы уверены?', reply_markup = keyboard.as_markup())


@router.callback_query(RequestActionMerchant.filter(F.accept == 2))
async def accept(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController, bot: Bot):
    await bot_query.change_status(callback_data.request_id, RequestStatus.accept_merchant)
    await query.message.delete()
    request = await bot_query.get_request(callback_data.request_id)
    await RequestNotification(request, bot_query.get_user(), bot).accept()


@router.callback_query(RequestActionMerchant.filter(F.transfer == 1))
async def pre_transfer(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                       bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text = f"Да", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            transfer = 2
        ).pack()),
        InlineKeyboardButton(text = f"Нет", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            main = 1
        ).pack())
    )
    await query.message.edit_text(text = 'Вы отправили?', reply_markup = keyboard.as_markup())


@router.callback_query(RequestActionMerchant.filter(F.transfer == 2))
async def transfer(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController, bot: Bot):
    await bot_query.change_status(callback_data.request_id, RequestStatus.transfer_merchant)
    await query.message.delete()
    request = await bot_query.get_request(callback_data.request_id)
    await RequestNotification(request, bot_query.get_user(), bot).transfer()


@router.callback_query(RequestActionMerchant.filter(F.message == 1))
async def pre_send_message(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                           state: FSMContext):
    await state.set_state(RequestMessage.text)
    await state.update_data(request_id = callback_data.request_id)
    await query.message.answer("Напишите сообщение.")


@router.message(RequestMessage.text)
async def send_requisites(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    text = message.text
    message = await bot_query.create_message((await state.get_data())['request_id'], text, MessageSender.merchant)
    request = await bot_query.get_request((await state.get_data())['request_id'])
    await RequestNotification(request, bot_query.get_user(), bot).send_message(message)


@router.callback_query(RequestActionMerchant.filter(F.cancel == 1))
async def pre_cancel(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController,
                     bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text = f"Да", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            cancel = 2
        ).pack()),
        InlineKeyboardButton(text = f"Нет", callback_data = RequestActionMerchant(
            request_id = callback_data.request_id,
            main = 1
        ).pack())
    )
    await query.message.edit_text(text = 'Вы уверены? что хотите отменить?', reply_markup = keyboard.as_markup())


@router.callback_query(RequestActionMerchant.filter(F.cancel == 2))
async def cancel(query: CallbackQuery, callback_data: RequestActionMerchant, bot_query: BotQueryController, bot: Bot):
    request = await bot_query.get_request(callback_data.request_id)
    await bot_query.cancel_request(callback_data.request_id)
    await query.message.delete()
    await RequestNotification(request, bot_query.get_user(), bot).cancel()
