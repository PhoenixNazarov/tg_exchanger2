import uuid

from aiogram import Router, F, Bot
from aiogram.filters import Command, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, ContentType
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import MessageSender
from database.enums import RequestStatus
from services.bot_query import BotQueryController
from ..request import RequestNotification, RequestActionUser

router = Router()


class RequestMessageUser(StatesGroup):
    text = State()


@router.message(Command(commands='requests_user'))
async def show_requests(message: Message, bot_query: BotQueryController, bot: Bot):
    requests = await bot_query.get_my_requests(False)
    for i in requests:
        await RequestNotification(i, bot_query.get_user(), bot).send_user_request()


# STATUS
@router.callback_query(RequestActionUser.filter(F.transfer == 1))
async def pre_transfer(query: CallbackQuery, callback_data: RequestActionUser, bot_query: BotQueryController, bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=RequestActionUser(
            request_id=callback_data.request_id,
            transfer=2
        ).pack()),
        InlineKeyboardButton(text=f"Нет", callback_data=RequestActionUser(
            request_id=callback_data.request_id,
            main=1
        ).pack())
    )
    await query.message.edit_text(text='Вы уверены?', reply_markup=keyboard.as_markup())


@router.callback_query(RequestActionUser.filter(F.transfer == 2))
async def transfer(query: CallbackQuery, callback_data: RequestActionUser, bot_query: BotQueryController, bot: Bot):
    await bot_query.change_status(callback_data.request_id, RequestStatus.transfer_user)
    await query.message.delete()
    request = await bot_query.get_request(callback_data.request_id)
    await RequestNotification(request, bot_query.get_user(), bot).transfer()


@router.callback_query(RequestActionUser.filter(F.message == 1))
async def pre_send_message(query: CallbackQuery, callback_data: RequestActionUser, bot_query: BotQueryController,
                           state: FSMContext):
    await state.set_state(RequestMessageUser.text)
    await state.update_data(request_id=callback_data.request_id)
    await query.message.answer("Напишите сообщение. Или отправьте документ(Фото без сжатия)")


@router.message(and_f(RequestMessageUser.text, F.content_type == ContentType.TEXT))
async def send_requisites(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    text = message.text
    message = await bot_query.create_message((await state.get_data())['request_id'], text, MessageSender.user)
    request = await bot_query.get_request((await state.get_data())['request_id'])
    await RequestNotification(request, bot_query.get_user(), bot).send_message(message)


@router.message(and_f(RequestMessageUser.text, F.content_type == ContentType.DOCUMENT))
async def send_requisites(message: Message, bot_query: BotQueryController, bot: Bot, state: FSMContext):
    name = f"images/{uuid.uuid4()}.{message.document.mime_type.split('/')[-1]}"
    await bot.download(message.document.file_id, name)
    message = await bot_query.create_message((await state.get_data())['request_id'], name, MessageSender.user)
    request = await bot_query.get_request((await state.get_data())['request_id'])
    await RequestNotification(request, bot_query.get_user(), bot).send_message(message, document=True)


@router.callback_query(RequestActionUser.filter(F.cancel == 1))
async def pre_cancel(query: CallbackQuery, callback_data: RequestActionUser, bot_query: BotQueryController,
                     bot: Bot):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=f"Да", callback_data=RequestActionUser(
            request_id=callback_data.request_id,
            cancel=2
        ).pack()),
        InlineKeyboardButton(text=f"Нет", callback_data=RequestActionUser(
            request_id=callback_data.request_id,
            main=1
        ).pack())
    )
    await query.message.edit_text(text='Вы уверены? что хотите отменить?', reply_markup=keyboard.as_markup())


@router.callback_query(RequestActionUser.filter(F.cancel == 2))
async def cancel(query: CallbackQuery, callback_data: RequestActionUser, bot_query: BotQueryController, bot: Bot):
    request = await bot_query.get_request(callback_data.request_id)
    await bot_query.cancel_request(callback_data.request_id)
    await query.message.delete()
    await RequestNotification(request, bot_query.get_user(), bot).cancel()
