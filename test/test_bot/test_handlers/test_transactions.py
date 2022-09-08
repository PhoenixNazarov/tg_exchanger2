import pytest
import pytest_asyncio
from aiogram.fsm.context import StorageKey
from aiogram.types import Message

from bot.database.models import TransStatus
from bot.messages.transactions import ControlTransUser, ControlTransMerch
from fake_updates.private_messages import generate_message, generate_query

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


@pytest_asyncio.fixture(scope = 'function')
async def new_trans(dp, bot):
    await dp.feed_update(bot, generate_message('/newtrans'))
    await dp.feed_update(bot, generate_message('THB'))
    await dp.feed_update(bot, generate_message('RUB'))
    await dp.feed_update(bot, generate_message('200'))
    await dp.feed_update(bot, generate_message('36'))
    await dp.feed_update(bot, generate_message('Cash by code'))


async def test_public(dp, bot, new_trans, setup_user_merchant_trans):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))
    assert isinstance(transaction_id, int)
    assert isinstance(message, Message)
    assert isinstance(user_message, Message)


async def test_take(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))
    merchant_message, user_message = await dp.feed_update(bot,
                                                          generate_query(message,
                                                                         f"mer_channel:{transaction_id}:True:False",
                                                                         merchant_id))
    assert isinstance(merchant_message, Message)
    assert isinstance(user_message, Message)


async def test_accept_merchant_user(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))
    merchant_message, user_message = await dp.feed_update(bot,
                                                          generate_query(message,
                                                                         f"mer_channel:{transaction_id}:True:False",
                                                                         merchant_id))
    await dp.feed_update(bot, generate_query(merchant_message, f"my_trans_merch:{transaction_id}:1:0:0:0", merchant_id))
    await dp.feed_update(bot, generate_query(merchant_message, f"my_trans_merch:{transaction_id}:0:0:1:0", merchant_id))
    transaction = await dp.feed_update(bot,
                                       generate_query(merchant_message, f"my_trans_merch:{transaction_id}:0:0:2:0",
                                                      merchant_id))
    assert transaction.status == TransStatus.wait_good_user

    await dp.feed_update(bot, generate_query(user_message, f"my_trans_user:{transaction_id}:0:0:0:0:1:0"))
    status = await dp.feed_update(bot, generate_query(user_message, f"my_trans_user:{transaction_id}:0:0:0:0:2:0"))
    assert status == 'finish'


async def test_edit_1_2(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))

    user_message = await dp.feed_update(bot, generate_message('/mytrans'))
    user_message = user_message[0]
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 1).pack()))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 2).pack()))
    await dp.feed_update(bot, generate_message('300'))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 3).pack()))
    await dp.feed_update(bot, generate_message('37'))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 4).pack()))
    await dp.feed_update(bot, generate_message('7300'))
    merchant_message, user_message = await dp.feed_update(bot,
                                                          generate_query(message,
                                                                         f"mer_channel:{transaction_id}:True:False",
                                                                         merchant_id))

    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 1).pack()))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 2).pack()))
    await dp.feed_update(bot, generate_message('200'))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 3).pack()))
    await dp.feed_update(bot, generate_message('38'))
    await dp.feed_update(bot, generate_query(user_message,
                                             ControlTransUser(id_transaction = transaction_id, edit = 4).pack()))
    await dp.feed_update(bot, generate_message('7600'))

    transaction = await dp.feed_update(bot,
                                       generate_query(merchant_message, f"my_trans_merch:{transaction_id}:0:0:2:0",
                                                      merchant_id))

    status = await dp.feed_update(bot, generate_query(user_message, f"my_trans_user:{transaction_id}:0:0:0:0:2:0"))
    assert status == 'finish'


async def test_send_message(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))

    merchant_message, user_message = await dp.feed_update(bot,
                                                          generate_query(message,
                                                                         f"mer_channel:{transaction_id}:True:False",
                                                                         merchant_id))

    _user_message = await dp.feed_update(bot, generate_message('/mytrans'))
    _user_message = _user_message[0]
    await dp.feed_update(bot, generate_query(_user_message,
                                             ControlTransUser(id_transaction = transaction_id, message = 1).pack()))
    await dp.feed_update(bot, generate_message('hello 1'))
    await dp.feed_update(bot, generate_message('hello 2'))
    await dp.feed_update(bot, generate_message('7300'))

    _merch_message = await dp.feed_update(bot, generate_message('/mytrans', merchant_id))
    _merch_message = _merch_message[0]

    await dp.feed_update(bot, generate_query(_merch_message,
                                             ControlTransMerch(id_transaction = transaction_id, message = 1).pack(), merchant_id))
    await dp.feed_update(bot, generate_message('hello 4', merchant_id))
    await dp.feed_update(bot, generate_message('hello 5', merchant_id))
    await dp.feed_update(bot, generate_message('73005', merchant_id))

    transaction = await dp.feed_update(bot,
                                       generate_query(merchant_message, f"my_trans_merch:{transaction_id}:0:0:2:0",
                                                      merchant_id))

    status = await dp.feed_update(bot, generate_query(user_message, f"my_trans_user:{transaction_id}:0:0:0:0:2:0"))
    assert status == 'finish'


async def test_cancel_trans_1(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))

    _user_message = await dp.feed_update(bot, generate_message('/mytrans'))
    _user_message = _user_message[0]
    await dp.feed_update(bot, generate_query(_user_message,
                                             ControlTransUser(id_transaction = transaction_id, cancel = 1).pack()))
    await dp.feed_update(bot, generate_query(_user_message,
                                             ControlTransUser(id_transaction = transaction_id, cancel = 2).pack()))


async def test_cancel_trans_2(dp, bot, new_trans, setup_user_merchant_trans, merchant_id):
    transaction_id, message, user_message = await dp.feed_update(bot, generate_message('Public'))
    merchant_message, user_message = await dp.feed_update(bot,
                                                          generate_query(message,
                                                                         f"mer_channel:{transaction_id}:True:False",
                                                                         merchant_id))
    _user_message = await dp.feed_update(bot, generate_message('/mytrans'))
    _user_message = _user_message[0]
    await dp.feed_update(bot, generate_query(_user_message,
                                             ControlTransUser(id_transaction = transaction_id, cancel = 1).pack()))
    await dp.feed_update(bot, generate_query(_user_message,
                                             ControlTransUser(id_transaction = transaction_id, cancel = 2).pack()))

