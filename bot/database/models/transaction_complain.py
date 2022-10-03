from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Boolean, Text
from sqlalchemy.orm import relationship, backref

from .base import BaseModelWithId
from .transaction_const import *


class TransactionComplain(BaseModelWithId):
    __tablename__ = 'transaction_complain'

    # transaction_id = Column(ForeignKey('transactions.id'), nullable = False)

    merchant_complain = Column(Boolean, nullable = False)
    cause = Column(Text)

    transaction = relationship('Transaction', back_populates = 'complain', lazy='selectin', uselist = False)

    async def to_json(self):
        return {
            'merchant_complain': self.merchant_complain,
            'cause': self.cause
        }
