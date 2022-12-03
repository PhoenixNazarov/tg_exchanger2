from typing import Optional

from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.enums import RequestStatus, Currency
from database.models import RequestModel, UserModel, RequestMessageModel, MessageSender


class RequestStatusException(Exception):
    pass


class RequestPermException(Exception):
    pass


class RequestActionMerchantRate(CallbackData, prefix="reqrate"):
    bid_id: int
    amount: int = None
    currency: Currency = None
    user_id: int = None

    accept: Optional[int] = None
    cancel: Optional[int] = None


class RequestActionUserRate(CallbackData, prefix="reqrateu"):
    bid_id: int
    amount: int = None
    currency: Currency = None
    rate: float = None

    accept: Optional[int] = None
    cancel: Optional[int] = None


class RequestActionUser(CallbackData, prefix="req_usr_act"):
    request_id: int
    main: Optional[int] = None
    transfer: Optional[int] = None
    message: Optional[int] = None
    cancel: Optional[int] = None


class RequestActionMerchant(CallbackData, prefix="req_mer_act"):
    request_id: int
    main: Optional[int] = None
    request: Optional[int] = None
    requisites: Optional[int] = None

    accept: Optional[int] = None
    transfer: Optional[int] = None

    message: Optional[int] = None
    cancel: Optional[int] = None


class RequestNotification:
    def __init__(self, request: RequestModel, user: UserModel, bot: Bot):
        self.__request = request
        self.__user = user
        self.__bot = bot

    async def send_user_request(self):
        text = f'Заявка #{self.__request.id}' \
               f'\n\nВы отдаёте: {self.__request.amount_in} {self.__request.currency_in}' \
               f'\nВы получаете: {self.__request.amount_out} {self.__request.currency_out}' \
               f'\nКурс: {self.__request.rate}' \
               f'\n\nСтатус: {self.__request.status}' \
               f'\n\nВаши реквизиты: {self.__request.user_requisites}' \
               f'\nРеквизиты пользователя: {self.__request.merchant_requisites}'

        keyboard = InlineKeyboardBuilder()

        if self.__request.status == RequestStatus.requisites_merchant:
            keyboard.row(InlineKeyboardButton(text=f"Оплатил", callback_data=RequestActionUser(
                request_id=self.__request.id,
                transfer=1
            ).pack()))

        keyboard.row(InlineKeyboardButton(text=f"Отправить сообщение", callback_data=RequestActionUser(
            request_id=self.__request.id,
            message=1
        ).pack()))

        if self.__request.status in [RequestStatus.request_user, RequestStatus.request_merchant,
                                     RequestStatus.request_merchant]:
            keyboard.row(InlineKeyboardButton(text=f"Отменить", callback_data=RequestActionUser(
                request_id=self.__request.id,
                cancel=1
            ).pack()))

        await self.__bot.send_message(chat_id=self.__get_user(), text=text, reply_markup=keyboard.as_markup())

    async def send_merchant_request(self):
        text = f'Заявка #{self.__request.id}' \
               f'\n\nВы отдаёте: {self.__request.amount_out} {self.__request.currency_out}' \
               f'\nВы получаете: {self.__request.amount_in} {self.__request.currency_in}' \
               f'\nКурс: {self.__request.rate}' \
               f'\n\nСтатус: {self.__request.status}' \
               f'\n\nРеквизиты пользователя: {self.__request.user_requisites}'

        keyboard = InlineKeyboardBuilder()

        if self.__request.status == RequestStatus.request_user:
            keyboard.row(InlineKeyboardButton(text=f"Принять", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                request=1
            ).pack()))
            keyboard.row(InlineKeyboardButton(text=f"Отклонить", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                cancel=1
            ).pack()))
        elif self.__request.status == RequestStatus.request_merchant:
            keyboard.row(InlineKeyboardButton(text=f"Отправить реквизиты", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                requisites=1
            ).pack()))
        elif self.__request.status == RequestStatus.transfer_user:
            keyboard.row(InlineKeyboardButton(text=f"Получил", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                accept=1
            ).pack()))
        elif self.__request.status == RequestStatus.accept_merchant:
            keyboard.row(InlineKeyboardButton(text=f"Отправил", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                transfer=1
            ).pack()))

        keyboard.row(InlineKeyboardButton(text=f"Отправить сообщение", callback_data=RequestActionMerchant(
            request_id=self.__request.id,
            message=1
        ).pack()))
        if self.__request.status in [RequestStatus.request_merchant, RequestStatus.request_merchant]:
            keyboard.row(InlineKeyboardButton(text=f"Отменить", callback_data=RequestActionMerchant(
                request_id=self.__request.id,
                cancel=1
            ).pack()))

        await self.__bot.send_message(chat_id=self.__get_merchant(), text=text, reply_markup=keyboard.as_markup())

    async def __send_user(self, text, keyboard=None):
        await self.__bot.send_message(chat_id=self.__get_user(), text=text, reply_markup=keyboard)

    async def __send_merchant(self, text, keyboard=None):
        await self.__bot.send_message(chat_id=self.__get_merchant(), text=text, reply_markup=keyboard)

    def __get_merchant(self):
        return self.__request.merchant_id

    def __get_user(self):
        return self.__request.user_id

    async def request(self):
        """ user, merchant """

        if self.__user.id == self.__get_user():
            await self.__user_request()
        else:
            await self.__merchant_request()

    async def __user_request(self):
        """ -> request_user -> request_merchant """

        await self.__send_user("Заявка успешно отправлена."
                               f"\nКак только пользователь @{self.__request.merchant.username} подтвердит или отклонит обмен."
                               f"ты получишь об этом уведомление"
                               f"\n\nПосле 15 минут ожидания, заявка будет считаться истекшей, пользователь не сможет принять её.")
        await self.__send_merchant(f"Поступила новая заявка на обмен от пользователя {self.__request.user.username}.")
        await self.send_merchant_request()

    async def __merchant_request(self):
        """ request_user -> request_merchant -> requisites_merchant"""

        await self.__send_user(f"Пользователь @{self.__request.merchant.username} принял твою заявку на обмен.")
        await self.send_user_request()

        await self.__send_merchant(f"Вы приняли заявку на обмен.")
        await self.send_merchant_request()

    async def cancel(self):
        """ user, merchant """
        if self.__user.id == self.__request.user_id:
            await self.__send_user(f"Вы отменили заявку")
            await self.__send_merchant(f"Пользователь отменил заявку")
        else:
            await self.__send_merchant(f"Вы отменили заявку")
            await self.__send_user(f"Пользователь отменил заявку")

    async def send_requisites(self):
        """ merchant , request_merchant -> requisites_merchant -> transfer_user """

        await self.__send_user(f"Пользователь @{self.__request.merchant.username} отправил реквизиты для перевода")
        await self.send_user_request()

        await self.__send_merchant(f"Вы отправили реквизиты для перевода")
        await self.send_merchant_request()

    async def transfer(self):
        """ user, merchant """

        if self.__user.id == self.__get_user():
            await self.__user_transfer()
        else:
            await self.__merchant_transfer()

    async def __user_transfer(self):
        """ requisites_merchant -> transfer_user -> accept_merchant """

        await self.__send_user(f"Вы подтвердили")
        await self.send_user_request()

        await self.__send_merchant(f"Пользователь подтвердил перевод")
        await self.send_merchant_request()

    async def __merchant_transfer(self):
        """ accept_merchant -> transfer_merchant -> """

        await self.__send_user(f"Пользователь получил перевод")
        await self.send_user_request()

        await self.__send_merchant(f"Вы подтвердили перевод")
        await self.send_merchant_request()

    async def accept(self):
        """ merchant, transfer_user -> accept_merchant -> transfer_merchant """

        await self.__send_user(f"Пользователь отправил")
        await self.send_user_request()

        await self.__send_merchant(f"Вы подтвердили")
        await self.send_merchant_request()

    # messages
    async def send_message(self, message: RequestMessageModel):
        keyboard_user = InlineKeyboardBuilder()
        keyboard_user.row(InlineKeyboardButton(text=f"Ответить", callback_data=RequestActionUser(
            request_id=self.__request.id,
            message=1
        ).pack()))
        keyboard_merchant = InlineKeyboardBuilder()

        keyboard_merchant.row(InlineKeyboardButton(text=f"Ответить", callback_data=RequestActionMerchant(
            request_id=self.__request.id,
            message=1
        ).pack()))

        if message.sender == MessageSender.merchant:
            await self.__send_user(f"Вы получили сообщение: \n\n{message.text}")
            await self.send_user_request()

            await self.__send_merchant(f"Сообщение отправлено")
        elif message.sender == MessageSender.user:
            await self.__send_merchant(f"Вы получили сообщение: \n\n{message.text}")
            await self.send_merchant_request()

            await self.__send_user(f"Сообщение отправлено")
        else:
            await self.__send_user(f"Вы получили сообщение: \n\n{message.text}")
            await self.send_user_request()

            await self.__send_merchant(f"Вы получили сообщение: \n\n{message.text}")
            await self.send_merchant_request()
