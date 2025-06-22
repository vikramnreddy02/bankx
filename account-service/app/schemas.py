from pydantic import BaseModel, EmailStr, condecimal

class AccountCreate(BaseModel):
    email: EmailStr
    initial_balance: condecimal(ge=0)

class Deposit(BaseModel):
    email: EmailStr
    amount: condecimal(gt=0)  # must be >0

class BalanceOut(BaseModel):
    email: EmailStr
    balance: condecimal(ge=0)

    class Config:  # ← This must be indented inside BalanceOut
        orm_mode = True

Withdraw = Deposit

