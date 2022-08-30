from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Text
from .base import BaseModelWithId

from .transaction_const import *


class TransactionModerate(BaseModelWithId):
    __tablename__ = 'transactions_moderate'

    user_id = Column(ForeignKey('users.id'), nullable = False)

    have_amount = Column(Float, nullable = False)
    have_currency = Column(Enum(Currency), nullable = False)
    get_amount = Column(Float, nullable = False)
    get_currency = Column(Enum(Currency), nullable = False)
    rate = Column(Float, nullable = False)

    commission_user = Column(Float, nullable = False)
    commission_merchant = Column(Float, nullable = False)

    get_thb_type = Column(Enum(TransGet), nullable = False)

    option1 = Column(Text)
    option2 = Column(Text)
    option3 = Column(Text)

    def __init__(self, amount, have_currency, get_currency, rate, auth_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.have_amount = amount
        self.have_currency = have_currency
        self.get_currency = get_currency
        self.rate = rate

        calculate_transaction_get_amount(self, auth_user)

