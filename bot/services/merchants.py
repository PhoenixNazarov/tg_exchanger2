from typing import Optional

from bot.database.models import Merchant, MerchantCommission, User
from .query_controller import QueryController

from bot.config_reader import config


async def add_merchant(session: QueryController, user_id: int) -> Merchant:
    user: User = await session(User).get_model(user_id)
    if user is None:
        raise Exception('User should write the bot')  # todo
    if len(user.transactions) != 0:
        raise Exception('User have not final transaction and can not become merchant')  # todo
    if user.id in config.merchants:
        raise Exception('User already is merchant')  # todo

    merchant = Merchant(id = user.id)
    config.merchants.append(merchant.id)
    await session(merchant).add_model()
    await session(MerchantCommission(id = merchant.id)).add_model()
    return merchant


async def get_merchants(session: QueryController) -> list[Merchant]:
    return await session(Merchant).get_models()


# async def get_merchant(session: QueryController, user_id: int) -> Optional[Merchant]:
#     return await session(Merchant).get_models()
