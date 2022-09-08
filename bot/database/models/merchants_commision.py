from sqlalchemy import Column, Integer, Float, ForeignKey
from .base import BaseModel


class MerchantCommission(BaseModel):
    __tablename__ = 'merchants_commission'

    id = Column(ForeignKey('merchants.id', ondelete='CASCADE'), nullable = False, unique = True, primary_key = True)

    usd = Column(Float, default = 0.0)
    thb = Column(Float, default = 0.0)
    rub = Column(Float, default = 0.0)

    def __int__(self, id):
        self.id = id
