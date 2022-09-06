from sqlalchemy import Column, Integer, BigInteger, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(BigInteger, nullable = False, unique = True, primary_key = True)

    language = Column(Text, nullable = False)
    username = Column(Text, nullable = False, unique = True)
    first_name = Column(Text, nullable = True)
    last_name = Column(Text, nullable = True)

    phone = Column(Text, nullable = True, unique = True)
    auth = Column(Boolean, default = False)

    good_transactions = Column(Integer, default = 0)
    bad_transactions = Column(Integer, default = 0)

    ban_time = Column(Integer, default = 0)

    transactions = relationship('Transaction', backref = 'User', lazy = 'selectin')
    merchant = relationship('Merchant', backref = 'User', lazy = 'selectin', uselist = False)
