from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Text
from .base import BaseModelWithId


class RequisitesCash(BaseModelWithId):
    __tablename__ = 'transactions_requisites_cash'

    transaction_id = Column(ForeignKey('transactions.id'), nullable = True)
    transaction_archive_id = Column(ForeignKey('transactions_archive.id'), nullable = True)
    town = Column(Text, nullable = False)
    region = Column(Text, nullable = False)


class RequisitesBankBalance(BaseModelWithId):
    __tablename__ = 'transactions_requisites_bankBalance'

    transaction_id = Column(ForeignKey('transactions.id'), nullable = True)
    transaction_archive_id = Column(ForeignKey('transactions_archive.id'), nullable = True)
    bank_name = Column(Text, nullable = False)
    number = Column(Integer, nullable = False)
    name = Column(Text, nullable = False)
