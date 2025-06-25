# app/main.py  ─────────────────────────────────────────────────────────────
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx, asyncio, traceback, json

from . import models, schemas
from .database import Base, engine, get_db

# ─────────────────────────── DB ────────────────────────────
Base.metadata.create_all(bind=engine)

app    = FastAPI()
router = APIRouter(prefix="/transaction", tags=["transaction"])

ACCOUNT_SVC = "http://account-service:80/account"

# ─────────────────────── HELPER HTTP CALL ──────────────────
async def _account_call(method: str, path: str, *, json=None) -> dict:
    """Wrapper → maps httpx/network errors to 502, keeps business errors intact."""
    try:
        async with httpx.AsyncClient(verify=False, timeout=5) as c:
            r = await c.request(method, f"{ACCOUNT_SVC}{path}", json=json)

    except httpx.RequestError as exc:                              # DNS, timeout, conn-reset…
        raise HTTPException(status.HTTP_502_BAD_GATEWAY,
                            f"account-service unavailable: {exc!s}")

    # surface 4xx/5xx from account-service directly
    if r.status_code >= 400:
        # try to relay JSON {detail: ...} nicely
        try:
            detail = r.json().get("detail", r.text)
        except json.JSONDecodeError:
            detail = r.text or f"account-service error {r.status_code}"
        raise HTTPException(r.status_code, detail)

    return r.json()

# ───────────────────────── ROUTES ──────────────────────────
@router.post("/", status_code=201, response_model=schemas.TransactionOut)
async def create_transaction(txn: schemas.TransactionCreate,
                             db: Session = Depends(get_db)):
    """
    Money transfer: withdraw from sender, deposit to receiver atomically
    (best-effort rollback if one side fails).
    """
    if txn.amount <= 0:
        raise HTTPException(400, "Amount must be greater than 0")

    # 1️⃣ make sure sender has enough money
    bal = await _account_call("GET", f"/balance/{txn.sender_email}")
    if float(bal["balance"]) < txn.amount:
        raise HTTPException(400, "Insufficient funds")

    #
    # 2️⃣ withdraw & deposit ─ run sequentially so we can roll back cleanly.
    #
    try:
        await _account_call("POST", "/withdraw", json={
            "email": txn.sender_email, "amount": txn.amount
        })
        await _account_call("POST", "/deposit", json={
            "email": txn.receiver_email, "amount": txn.amount
        })
    except HTTPException as deposit_err:
        # 🔄 rollback sender withdrawal (best-effort, ignore rollback failure)
        try:
            await _account_call("POST", "/deposit", json={
                "email": txn.sender_email, "amount": txn.amount
            })
        except Exception:          # swallow – we’re already failing
            pass
        raise deposit_err          # propagate original problem

    #
    # 3️⃣ store the transaction locally
    #
    row = models.Transaction(**txn.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get(
    "/recent/{email}",
    response_model=list[schemas.TransactionOut],   # ← list of Txn objects
    status_code=200,
)
def recent_transactions(
    email: str,
    db: Session = Depends(get_db),
):
    """
    Return the 10 most-recent transfers **involving** the given email
    (either as sender OR receiver), sorted newest → oldest.
    """
    rows = (
        db.query(models.Transaction)
        .filter(
            (models.Transaction.sender_email == email)
            | (models.Transaction.receiver_email == email)
        )
        .order_by(models.Transaction.id.desc())   # latest first
        .limit(10)
        .all()
    )
    return rows

@router.get("/health", tags=["internal"])
def health():
    return {"status": "ok"}

app.include_router(router)

