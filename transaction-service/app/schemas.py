from pydantic import BaseModel, EmailStr
from datetime import datetime

class TransactionCreate(BaseModel):
    sender_email: EmailStr
    receiver_email: EmailStr
    amount: float

class TransactionOut(BaseModel):
    id: int
    sender_email: EmailStr
    receiver_email: EmailStr
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True
