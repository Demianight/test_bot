from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer)
    balance = Column(Integer)

    requests = relationship('Request', back_populates='owner')

    def __repr__(self):
        return f'{self.id} {self.tg_id}'


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    platform = Column(String)
    budget = Column(ARRAY(Integer))
    phone = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship('User', back_populates='requests')

    def __repr__(self):
        return (
            f'New Нrequest number {self.id}\n'
            f'Customer has {self.type} company\n'
            f'He needs bot in {self.platform}\n'
            f'He has budget of {self.budget}\n'
            f'His phone number is {self.phone}\n'
        )
