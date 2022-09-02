from typing import Optional

from bot.database.models import User
from .query_controller import QueryController


async def create_user(session: QueryController,
                      user_id: int,
                      first_name: str,
                      last_name: str,
                      username: str,
                      language: str) -> User:
    user_model = User(
        id = user_id,
        first_name = first_name,
        last_name = last_name,
        username = username,
        language = language
    )
    return await session(user_model).add_model()


async def get_user(session: QueryController, user_id: int) -> Optional[User]:
    return await session(User).get_model(user_id)


async def update_user(session: QueryController, user_model: User, data: dict) -> Optional[User]:
    await session(user_model).update_model_values(
        data
    )
    return user_model
