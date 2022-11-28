from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base


class MerchantModel(Base):
    __tablename__ = 'merchant'

    id = Column(ForeignKey('user.id'), nullable = False, unique = True, primary_key = True)
    username = Column(String(32))
    sleep = Column(Boolean, default = False)

    max_count_bids = Column(Integer, default = 2)
    max_count_requests = Column(Integer, default = 2)
    max_amount_bid = Column(Numeric(8, 2), default = 2)

    user = relationship("UserModel", back_populates = "merchant", lazy = 'joined', uselist = False)
    requests = relationship("RequestModel", back_populates = "merchant", lazy = 'selectin')
    bids = relationship("BidModel", back_populates = "merchant", lazy = 'selectin')
