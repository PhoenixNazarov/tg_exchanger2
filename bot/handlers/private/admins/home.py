from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message

from bot.info import _  # todo remove
from bot.services.bot_query import BotQueryController
from bot.commands import set_admin_commands

router = Router()


@router.message(Command(commands = ['admin_help']))
async def admin_help(message: Message, bot_query: BotQueryController, bot: Bot):
    await message.answer(_('/admin_help'
                           '\n'
                           '\n/add_merch [id]'
                           '\n/del_merch [id]'
                           '\n/list_merch'
                           '\n/set_limit_amount [id] [value]'
                           '\n/set_accumulated_commission [id] (currency usd, thb, rub) (value) - default set 0 '
                           'in all currency'))
    await set_admin_commands(bot, bot_query.get_user().id, bot_query.get_user().language)


async def show_merchant(message: Message, merchant):
    await message.answer(text = _('Merchant:'
                                  '\n{merchant.id}'
                                  '\n{merchant.user.username}'
                                  '\nAllow amount: {merchant.allow_max_amount}'
                                  '\nAccumulated commission:'
                                  '\nUsd: {merchant.accumulated_commission.usd}'
                                  '\nThb: {merchant.accumulated_commission.thb}'
                                  '\nRub: {merchant.accumulated_commission.rub}').format(merchant = merchant))


@router.message(Command(commands = ['add_merch']))
async def add_merchant(message: Message, bot_query: BotQueryController):
    args = message.text.split()
    merchant = await bot_query.add_merchant(user_id = int(args[1]))
    await message.answer(text = _('Add merchant: {merchant.id}').format(merchant = merchant))


@router.message(Command(commands = ['list_merch']))
async def list_merchant(message: Message, bot_query: BotQueryController):
    merchants = await bot_query.get_merchants()
    for merch in merchants:
        await show_merchant(message, merch)
