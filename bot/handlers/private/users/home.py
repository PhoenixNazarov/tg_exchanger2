from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.info import _  # todo delete

router = Router()


@router.message(Command(commands = ['help']))
async def welcome(message: Message, state: FSMContext):
    await message.answer(text =
                         _('Main menu'
                           '\n'
                           '\nTransactions:'
                           '\n/newtrans - Create new transaction'
                           '\n/mytrans - Show my transactions'
                           '\n'
                           '\nRates:'
                           '\n/rates'), reply_markup = ReplyKeyboardRemove())
    await state.clear()
