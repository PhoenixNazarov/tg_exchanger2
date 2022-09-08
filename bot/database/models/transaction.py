from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.orm import relationship, backref

from .base import BaseModelWithId
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

    active = Column(Boolean, default = True)
    status = Column(Enum(TransStatus), default = TransStatus.in_stack)
    merchant_message_id = Column(Integer)

    get_thb_type = Column(Enum(TransGet), nullable = False)
    req_cash = relationship('RequisitesCash', backref = 'transactions', uselist = False)
    req_bank = relationship('RequisitesBankBalance', backref = 'transactions', uselist = False)

    messages = relationship('MessageTransaction', backref = backref('transactions', passive_deletes=True))

    maker = relationship('User', backref = 'Transaction', uselist = False, viewonly = True)
    merchant = relationship('Merchant', backref = 'Transaction', uselist = False, viewonly = True)

    async def to_json(self):
        out = {}
        if self.get_thb_type == TransGet.cash:
            out = {
                'cash_town': self.req_cash.town,
                'cash_region': self.req_cash.region
            }
        elif self.get_thb_type == TransGet.bank_balance:
            out = {
                'bank_name': self.req_bank.bank_name,
                'bank_number': self.req_bank.number,
                'bank_username': self.req_bank.name
            }
        out.update({
            'id': self.id,
            'user_id': self.user_id,
            'active': self.active,
            'merchant_id': self.merchant_id,
            'have_amount': self.have_amount,
            'have_currency': self.have_currency,
            'get_amount': self.get_amount,
            'get_currency': self.get_currency,
            'rate': self.rate,
            'commission_user': self.commission_user,
            'commission_merchant': self.commission_merchant,
            'status': self.status,
            'merchant_message_id': self.merchant_message_id,
            'get_thb_type': self.get_thb_type
        })
        return out
