from sqlalchemy import Column, Integer, Numeric, String
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id          = Column(Integer, primary_key=True, index=True)
    user_email  = Column(String, unique=True, index=True, nullable=False)
    balance     = Column(Numeric(12, 2), default=0)   # high-precision money

