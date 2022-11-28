from typing import Optional, List

from aiogram.types import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.enums import RequestStatus
from database.models import UserModel, BidModel, RequestModel, MerchantModel, MessageSender, RequestMessageModel


class BotQueryController:
    def __init__(self, session: AsyncSession):
        self._session = session

        self._user_tg: Optional[User] = None
        self._user: Optional[UserModel] = None

    # USER
    def get_user(self) -> UserModel:
        return self._user

    async def get_and_update_user(self, user: User):
        self._user_tg = user
        self._user: UserModel = await self._session.get(UserModel, self._user_tg.id)

        if not self._user:
            await self._create_user()
        else:
            self._user.username = self._user_tg.username
            self._user.first_name = self._user_tg.first_name
            self._user.last_name = self._user_tg.last_name
            await self._session.flush()

    async def _create_user(self):
        self._user = UserModel(id = self._user_tg.id, language = self._user_tg.language_code,
                               username = self._user_tg.username,
                               first_name = self._user_tg.first_name, last_name = self._user_tg.last_name)
        self._session.add(self._user)
        await self._session.flush()

    # BIDS
    async def get_bids(self) -> List[BidModel]:
        _bids = (await self._session.execute(select(BidModel))).all()
        bids = []
        for i in _bids:
            if i[0].merchant:
                if not i[0].merchant.sleep:
                    bids.append(i[0])
        return bids

    async def get_bid(self, bid_id: int) -> BidModel:
        return await self._session.get(BidModel, bid_id)

    # REQUESTS
    async def create_request(self, bid_id: int, requisites: str, amount_in: float = None,
                             amount_out: float = None) -> RequestModel:
        bid: BidModel = await self._session.get(BidModel, bid_id)
        request = RequestModel(merchant_id = bid.merchant.id, user_id = self._user.id,
                               description = bid.description, user_requisites = requisites,
                               currency_in = bid.currency_in, currency_out = bid.currency_out,
                               rate = bid.rate, amount_in = amount_in, amount_out = amount_out)
        self._session.add(request)
        await self._session.flush()
        request.merchant = await self._session.get(MerchantModel, request.merchant_id)
        return request

    async def cancel_request(self, request_id: int):
        request = await self.get_request(request_id)
        await self._session.delete(request)
        await self._session.flush()

    async def get_my_requests(self, merchant: bool = False) -> List[RequestModel]:
        if merchant:
            requests = (
                await self._session.execute(select(RequestModel).where(RequestModel.merchant_id == self._user_tg.id)
                                            .where(RequestModel.status.not_in([RequestStatus.transfer_merchant]))))
        else:
            requests = (
                await self._session.execute(select(RequestModel).where(RequestModel.user_id == self._user_tg.id)
                                            .where(RequestModel.status.not_in([RequestStatus.transfer_merchant]))))
        return [i[0] for i in requests]

    async def get_request(self, request_id: int) -> RequestModel:
        return await self._session.get(RequestModel, request_id)

    async def change_status(self, request_id: int, status: RequestStatus):
        request: RequestModel = await self._session.get(RequestModel, request_id)

        if request.status == status.prev():
            request.status = status
            await self._session.flush()

    async def set_merchant_requisites(self, request_id: int, requisites: str):
        request = await self._session.get(RequestModel, request_id)
        request.merchant_requisites = requisites
        await self._session.flush()

    async def create_message(self, request_id: int, text: str, sender: MessageSender) -> RequestMessageModel:
        message = RequestMessageModel(request_id = request_id, text = text, sender = sender)
        self._session.add(message)
        await self._session.flush()
        return message
