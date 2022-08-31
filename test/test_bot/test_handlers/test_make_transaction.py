import pytest
from aiogram.fsm.context import StorageKey

from fake_updates.private_messages import generate_message

pytestmark = pytest.mark.asyncio


async def test_new_trans1(dp, bot):
    await dp.feed_update(bot, generate_message('/newtrans'))
    await dp.feed_update(bot, generate_message('USDT'))

    assert await dp.storage.get_state(bot, StorageKey(bot.id, chat_id = 557060775,
                                                      user_id = 557060775)) == 'TransactionForm:amount'
    await dp.feed_update(bot, generate_message('THB'))
    await dp.feed_update(bot, generate_message('USDT'))
    await dp.feed_update(bot, generate_message('asd'))
    await dp.feed_update(bot, generate_message('rrr'))
    await dp.feed_update(bot, generate_message('-123'))
    await dp.feed_update(bot, generate_message('11.0000123'))
    await dp.feed_update(bot, generate_message('11.0000123 asdqwe'))
    await dp.feed_update(bot, generate_message('qwe11.0000123'))
    await dp.feed_update(bot, generate_message('-11.0000123'))
    await dp.feed_update(bot, generate_message('-11,0000123'))
    await dp.feed_update(bot, generate_message('-11,0000123'))
    assert await dp.storage.get_state(bot, StorageKey(bot.id, chat_id = 557060775,
                                                      user_id = 557060775)) == 'TransactionForm:amount'

    await dp.feed_update(bot, generate_message('1000'))
    trans = await dp.feed_update(bot, generate_message('36.5'))

    assert trans['have_currency'] == 'USDT'
    assert trans['get_currency'] == 'THB'
    assert trans['amount'] == 1000
    assert trans['rate'] == 36.5


async def test_new_trans_cash(dp, bot):
    await dp.feed_update(bot, generate_message('/newtrans'))
    await dp.feed_update(bot, generate_message('THB'))
    await dp.feed_update(bot, generate_message('USDT'))
    await dp.feed_update(bot, generate_message('100'))
    await dp.feed_update(bot, generate_message('36'))

    await dp.feed_update(bot, generate_message('Cash'))
    await dp.feed_update(bot, generate_message('Phuket'))
    trans = await dp.feed_update(bot, generate_message('Rawai'))

    assert trans['have_currency'] == 'THB'
    assert trans['get_currency'] == 'USDT'
    assert trans['amount'] == 100
    assert trans['rate'] == 36
    assert trans['type_receive_thb'] == 'cash'
    assert trans['cash_town'] == 'Phuket'
    assert trans['cash_region'] == 'Rawai'


async def test_new_trans_transfer(dp, bot):
    await dp.feed_update(bot, generate_message('/newtrans'))
    await dp.feed_update(bot, generate_message('THB'))
    await dp.feed_update(bot, generate_message('USDC'))
    await dp.feed_update(bot, generate_message('111'))
    await dp.feed_update(bot, generate_message('36'))

    await dp.feed_update(bot, generate_message('Transfer'))
    await dp.feed_update(bot, generate_message('Krungsri'))

    assert await dp.storage.get_state(bot, StorageKey(bot.id, chat_id = 557060775,
                                                      user_id = 557060775)) == 'TransactionForm:bank_number'
    await dp.feed_update(bot, generate_message('asd'))
    await dp.feed_update(bot, generate_message('-9570147158'))
    await dp.feed_update(bot, generate_message('1.1000000000'))
    await dp.feed_update(bot, generate_message('-1.1000000000'))
    await dp.feed_update(bot, generate_message('1'))
    assert await dp.storage.get_state(bot, StorageKey(bot.id, chat_id = 557060775,
                                                      user_id = 557060775)) == 'TransactionForm:bank_number'

    await dp.feed_update(bot, generate_message('9570147158'))
    trans = await dp.feed_update(bot, generate_message('Vova Nazarov'))

    assert trans['have_currency'] == 'THB'
    assert trans['get_currency'] == 'USDC'
    assert trans['amount'] == 111
    assert trans['rate'] == 36
    assert trans['type_receive_thb'] == 'bank_balance'
    assert trans['bank_name'] == 'Krungsri'
    assert trans['bank_number'] == '9570147158'
    assert trans['bank_username'] == 'Vova Nazarov'


async def test_new_trans_code(dp, bot):
    await dp.feed_update(bot, generate_message('/newtrans'))
    await dp.feed_update(bot, generate_message('THB'))
    await dp.feed_update(bot, generate_message('RUB'))
    await dp.feed_update(bot, generate_message('1112'))
    await dp.feed_update(bot, generate_message('36'))

    trans = await dp.feed_update(bot, generate_message('Cash by code'))

    assert trans['have_currency'] == 'THB'
    assert trans['get_currency'] == 'RUB'
    assert trans['amount'] == 1112
    assert trans['rate'] == 36
    assert trans['type_receive_thb'] == 'atm_machine'
