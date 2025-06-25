from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import asyncio, httpx

from . import models, schemas, auth
from .database import Base, engine, get_db

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter(prefix="/user", tags=["user"])

# ──────────────────────── ANALYTICS HELPER ───────────────────────
def _log_event_async(service: str, event_type: str, metadata: dict) -> None:
    """Fire-and-forget analytics call (never blocks endpoints)."""

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


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        email=user.email,
        hashed_password=auth.hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    _log_event_async(
        "user-service",
        "user_registered",
        {"email": db_user.email},
    )
    return {"email": db_user.email}


@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Authenticate a user with email & password (no JWT returned)."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(
        user.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    _log_event_async(
        "user-service",
        "user_login",
        {"email": user.email},
    )

    return {"message": "Login successful"}


# Health endpoint
@router.get("/health", tags=["internal"])
def health():
    return {"status": "ok"}


# Register router with FastAPI app
app.include_router(router)

