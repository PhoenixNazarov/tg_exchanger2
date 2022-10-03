from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.commands import set_user_commands
from bot.info import _  # todo delete
from bot.services.bot_query import BotQueryController

router = Router()


@router.message(Command(commands = ['help']))
async def welcome(message: Message, state: FSMContext, bot_query: BotQueryController, bot: Bot):
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
    await set_user_commands(bot, bot_query.get_user().id, bot_query.get_user().language)
