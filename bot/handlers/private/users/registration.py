from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from bot.info import _  # todo delete
from bot.services.bot_query import BotQueryController

from .home import welcome

router = Router()


class Authorized(StatesGroup):
    get_username = State()
    get_phone = State()


@router.message(or_f(CommandStart(), StateFilter(state = Authorized.get_username)))
async def send_pre_welcome(message: Message, state: FSMContext, bot_query: BotQueryController):
    if message.from_user.username is None:
        await message.answer(text =
                             _('Hi.\n\nYour username is not specified. We cannot authenticate you.\nAdd username and '
                               'write /start'))
        return await state.set_state(Authorized.get_username)
    elif bot_query.get_user() is None:
        await bot_query.create_user()
        return await send_contact(message, state)
    elif bot_query.get_user().phone is None:
        return await send_contact(message, state)
    else:
        return await welcome(message, state)


@router.message(((F.content_type == 'contact') & ~(F.phone is None)), StateFilter(state = Authorized.get_phone))
async def send_welcome_final(message: Message, state: FSMContext, bot_query: BotQueryController):
    await bot_query.set_phone(message.contact.phone_number)
    await welcome(message, state)


@router.message(StateFilter(state = Authorized.get_phone))
async def send_contact(message: Message, state: FSMContext):
    await state.set_state(Authorized.get_phone)
    await message.answer(text = _(
        'Hi.\n\nYou need to provide a phone number for authentication. So we will understand the seriousness of your '
        'applications'),
        reply_markup =
        ReplyKeyboardBuilder()
        .add(KeyboardButton(text = _('Ready to trade'), request_contact = True))
        .as_markup()
    )


