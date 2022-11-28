from sqlalchemy import Column, Integer, Numeric, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from .base import Base


class UserModel(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, nullable = False, unique = True, primary_key = True)
    proof = Column(Boolean)

    first_name = Column(String(64))
    last_name = Column(String(64))
    username = Column(String(32))
    language = Column(String(2))

    merchant = relationship("MerchantModel", back_populates = "user", lazy = 'joined', uselist=False)
    requests = relationship("RequestModel", back_populates = "user", lazy = 'selectin')

