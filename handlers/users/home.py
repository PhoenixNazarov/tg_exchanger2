from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from info import _  # todo delete

router = Router()
outer_router = Router()


@outer_router.message()
@router.message(Command(commands = ['help', 'start']))
async def welcome(message: Message, state: FSMContext, bot: Bot):
    await message.answer(text =
                         _("""
/show
/start
/faq
<b>Бот для безопасного обмена денег в Таиланде</b>💵

Тут можно быстро , а самое главное БЕЗОПАСНО обменять российские рубли, криптовалюту на тайские баты. Для безопасного обмена каждый мечант вносит страховой депозит. Каждый мерчант прошёл верефикацию и имеет статус проверенный. 

Как это работает: Вы выбираете мерчанта и переводите на указанный им счёт российские рубли или криптовалюту, после чего вы получаете тайские баты удобным для Вас способом. Удачного обмена🙏"""),
                         reply_markup = ReplyKeyboardRemove())

    await state.clear()


@outer_router.message()
@router.message(Command(commands = ['faq']))
async def welcome(message: Message, state: FSMContext, bot: Bot):
    await message.answer(text =
                         _("""
✅Друзья, хочу поделиться с вами практической информацией, как получить деньги с банкомата через систему cardless (без карты).
Вам нужен жёлтый банкомат
<b>Krungsri bank</b>
Они есть почти около каждого магазина 7/11 или <b>Family Mart</b>

• На экране справа внизу выбираете <b>Cardless Withdrawal/ATM</b>.

• Вводите номер телефона, который вам пришлют <b>Enter Mobile</b>.

• Вводите сумму <b>Enter Amount</b>.

• Вводите одноразовый 6-значный код, который вам пришлют <b>Withdrawal Code</b>.

• Все вышеперечисленные действия подтверждаем кнопкой <b>Correct</b>.

• Банкомат выдаст вам наличные баты! 

• Под этим постом прикладываю видео (https://t.me/obmenmartinsoull/6) с инструкцией!

• <b><u>Так или иначе вам помогут снять наличные, любым удобным для вас способом , по голосовой или видеосвязи.</u></b>"""),
                         reply_markup = ReplyKeyboardRemove())

    await state.clear()
