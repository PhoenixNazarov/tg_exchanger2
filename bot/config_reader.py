from typing import Optional, List
from pydantic import BaseSettings, validator, SecretStr, RedisDsn
from pathlib import Path


class Settings(BaseSettings):
    debug: bool
    test: bool
    db_test: str

    bot_token: SecretStr

    fsm_mode: str
    redis: Optional[RedisDsn]

    db: str

    admins: List[int]
    merchants: List[int]
    merchant_commission: float
    merchant_channel: int

    max_user_transaction: int

    @validator("fsm_mode")
    def fsm_type_check(cls, v):
        if v not in ("memory", "redis"):
            raise ValueError("Incorrect fsm_mode. Must be one of: memory, redis")
        return v

    @validator("redis")
    def skip_validating_redis(cls, v, values):
        if values["fsm_mode"] == "redis" and v is None:
            raise ValueError("Redis config is missing, though fsm_type is 'redis'")
        return v

    class Config:
        env_file = Path(__file__).parent.joinpath('.env')
        env_file_encoding = 'utf-8'


config = Settings()
