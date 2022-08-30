from typing import Optional

from bot.database.models import User as UserModel
from .query_controller import QueryController


async def create_user(session: QueryController,
                      user_id: int,
                      first_name: str,
                      last_name: str,
                      username: str,
                      language: str) -> UserModel:
    user_model = UserModel(
        id = user_id,
        first_name = first_name,
        last_name = last_name,
        username = username,
        language = language
    )
    return await session(user_model).add_model()


async def get_user(session: QueryController, user_id: int) -> Optional[UserModel]:
    return await session(UserModel).get_model(user_id)


async def update_user(session: QueryController, user_model: UserModel, data: dict) -> Optional[UserModel]:
    await session(user_model).update_model_values(
        data
    )
    return user_model
