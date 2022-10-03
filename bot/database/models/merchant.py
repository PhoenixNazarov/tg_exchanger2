from sqlalchemy import Column, Integer, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import BaseModel


class Merchant(BaseModel):
    __tablename__ = 'merchants'

    id = Column(ForeignKey('users.id'), nullable = False, unique = True, primary_key = True)
    active = Column(Boolean, default = True)

    accumulated_commission = relationship('MerchantCommission', backref = 'Merchant', lazy = 'selectin', uselist=False,
                                          passive_deletes=True)

    allow_max_amount = Column(Integer, default = 1000)
    good_transactions = Column(Integer, default = 0)
    bad_transactions = Column(Integer, default = 0)
    rating = Column(Integer, default = 0)

    user = relationship('User', back_populates = 'merchant', viewonly=True, uselist=False, lazy = 'selectin')
    transactions = relationship('Transaction', back_populates = 'merchant', lazy = 'selectin')

    def __int__(self, id):
        self.id = id
