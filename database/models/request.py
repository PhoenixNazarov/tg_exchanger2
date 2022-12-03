import time

import strenum
from sqlalchemy import Column, String, Numeric, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import Base
from ..enums import Currency, RequestStatus


class RequestModel(Base):
    __tablename__ = 'request'

    id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    merchant_id = Column(ForeignKey('merchant.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)

    description = Column(String(1024), nullable=False)
    user_requisites = Column(String(1024), nullable=False)
    merchant_requisites = Column(String(1024))

    currency_in = Column(Enum(Currency), nullable=False)
    currency_out = Column(Enum(Currency), nullable=False)

    rate = Column(Numeric(6, 2), nullable=False)

    amount_in = Column(Numeric(8, 2), nullable=False)
    amount_out = Column(Numeric(8, 2), nullable=False)

    status = Column(Enum(RequestStatus), default=RequestStatus.request_user)
    time_active = Column(BigInteger, default=lambda: int(time.time()))

    merchant = relationship("MerchantModel", back_populates="requests", lazy='joined', uselist=False)
    user = relationship("UserModel", back_populates="requests", lazy='joined', uselist=False)
    messages = relationship("RequestMessageModel", back_populates="request", lazy='selectin',
                            cascade="all,delete")


class MessageSender(strenum.StrEnum):
    merchant = 'merchant'
    user = 'user'
    admin = 'admin'


class RequestMessageModel(Base):
    __tablename__ = 'request_message'

    id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    request_id = Column(ForeignKey('request.id'), nullable=False)

    text = Column(String(1024), nullable=False)
    sender = Column(Enum(MessageSender), nullable=False)
    time_send = Column(BigInteger, default=lambda: int(time.time()))

    request = relationship("RequestModel", back_populates="messages", lazy='joined', uselist=False)
