# app/main.py  ─────────────────────────────────────────────────────
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import asyncio, httpx

from . import models, schemas
from .database import Base, engine, get_db

# ───────────────────────── DB TABLES ──────────────────────────────
Base.metadata.create_all(bind=engine)

app    = FastAPI()
router = APIRouter(prefix="/account", tags=["account"])

# ──────────────────────── ANALYTICS HELPER ───────────────────────
def _log_event_async(service: str, event_type: str, metadata: dict) -> None:
    """
    Non-blocking fire-and-forget analytics call.
    Executed in the *background* so endpoints stay fast.
    """
    async def _send() -> None:
        try:
            async with httpx.AsyncClient(verify=False, timeout=3) as c:
                await c.post(
                    "http://analytics-service:80/analytics/",
                    json={
                        "service": service,
                        "event_type": event_type,
                        "metadata": metadata,
                    },
                )
        except Exception as exc:  # swallow errors – analytics must never break prod
            print(f"[analytics] failed: {exc}")

    asyncio.create_task(_send())

# ─────────────────────────── ROUTES ──────────────────────────────
@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.BalanceOut,
)
async def create_account(
    acct: schemas.AccountCreate,
    db:   Session = Depends(get_db),
):
    """Create a brand-new account (with optional opening balance)."""
    if db.query(models.Account).filter(models.Account.user_email == acct.email).first():
        raise HTTPException(status_code=400, detail="Account already exists")

    row = models.Account(user_email=acct.email, balance=acct.initial_balance)
    db.add(row)
    db.commit()
    db.refresh(row)

    _log_event_async(
        "account-service",
        "account_created",
        {"email": acct.email, "balance": float(acct.initial_balance)},
    )
    return {"email": row.user_email, "balance": row.balance}


@router.post(
    "/deposit",
    status_code=status.HTTP_200_OK,
    response_model=schemas.BalanceOut,
)
async def deposit(
    dep: schemas.Deposit,
    db:  Session = Depends(get_db),
):
    """Deposit money into an existing account."""
    row = db.query(models.Account).filter(
        models.Account.user_email == dep.email
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Account not found")

    row.balance += dep.amount
    db.commit()
    db.refresh(row)

    _log_event_async(
        "account-service",
        "deposit",
        {"email": dep.email, "amount": float(dep.amount)},
    )
    return {"email": row.user_email, "balance": row.balance}


@router.get(
    "/balance/{email}",
    response_model=schemas.BalanceOut,
)
async def get_balance(email: str, db: Session = Depends(get_db)):
    row = db.query(models.Account).filter(
        models.Account.user_email == email
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"email": row.user_email, "balance": row.balance}


@router.post(
    "/withdraw",
    status_code=status.HTTP_200_OK,
    response_model=schemas.BalanceOut,
)
async def withdraw(
    pay: schemas.Withdraw,
    db: Session = Depends(get_db),
):
    """Withdraw money from an account (fails if insufficient balance)."""
    row = db.query(models.Account).filter_by(user_email=pay.email).first()
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")

    if row.balance < pay.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    row.balance -= pay.amount
    db.commit(); db.refresh(row)

    _log_event_async(
        "account-service",
        "withdraw",
        {"email": pay.email, "amount": float(pay.amount)},
    )
    return {"email": row.user_email, "balance": row.balance}



@router.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}

# Register routes with the FastAPI app
app.include_router(router)

