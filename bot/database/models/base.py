import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer

Base = declarative_base()


class EmptyBase(Base):
    __abstract__ = True

    def __repr__(self):
        return "<{0.__class__.__name__})>".format(self)


class BaseModel(EmptyBase):
    __abstract__ = True

    created_at = Column(Integer, nullable=False, default=int(time.time()))
    updated_at = Column(Integer, nullable=False, default=int(time.time()), onupdate=int(time.time()))

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={id(self)})>"


class BaseModelWithId(BaseModel):
    __abstract__ = True

    id = Column(Integer, nullable = False, unique = True, primary_key = True, autoincrement = True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)
