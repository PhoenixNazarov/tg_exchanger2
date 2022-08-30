from sqlalchemy import Column, Float, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship

from .base import BaseModelWithId
# from loader import _

from .transaction_const import *


class Transaction(BaseModelWithId):
    __tablename__ = 'transactions'

    user_id = Column(ForeignKey('users.id'), nullable = False)
    merchant_id = Column(ForeignKey('merchants.id'))

    have_amount = Column(Float, nullable = False)
    have_currency = Column(Enum(Currency), nullable = False)
    get_amount = Column(Float, nullable = False)
    get_currency = Column(Enum(Currency), nullable = False)
    rate = Column(Float, nullable = False)

    commission_user = Column(Float, nullable = False)
    commission_merchant = Column(Float, nullable = False)

    status = Column(Enum(TransStatus), default = TransStatus.in_stack)
    merchant_message_id = Column(Integer)

    get_thb_type = Column(Enum(TransGet), nullable = False)
    req_cash = relationship('RequisitesCash', backref = 'transactions', uselist = False)
    req_bank = relationship('RequisitesBankBalance', backref = 'transactions', uselist = False)

    messages = relationship('MessageTransaction', backref = 'transactions')

    maker = relationship('User', backref = 'Transaction', uselist = False, viewonly=True)
    merchant = relationship('Merchant', backref = 'Transaction', uselist = False, viewonly=True)
