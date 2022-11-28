from sqlalchemy import Column, String, Numeric, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import Base

from ..enums import Currency


class BidModel(Base):
    __tablename__ = 'bid'

    id = Column(BigInteger, nullable = False, unique = True, primary_key = True)
    merchant_id = Column(ForeignKey('merchant.id'), nullable = False)

    description = Column(String(1024))

    currency_in = Column(Enum(Currency), nullable = False)
    currency_out = Column(Enum(Currency), nullable = False)

    rate = Column(Numeric(6, 2), nullable = False)

    min_amount = Column(Numeric(8, 2), nullable = False)
    max_amount = Column(Numeric(8, 2), nullable = False)
    actual_amount = Column(Numeric(8, 2), nullable = False)

    merchant = relationship("MerchantModel", back_populates = "bids", lazy = 'joined', uselist=False)
