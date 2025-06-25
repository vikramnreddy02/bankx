from fastapi import FastAPI, APIRouter, Depends
from bson import ObjectId

from .schemas import EventCreate, EventOut
from .database import get_collection

# FastAPI app
app = FastAPI()

# Router prefix → /analytics/…
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/", response_model=EventOut)  # /analytics/
def record_event(event: EventCreate, collection=Depends(get_collection)):
    """Store a user-generated event in MongoDB."""
    result = collection.insert_one(event.dict())
    event_dict = event.dict()
    event_dict["id"] = str(result.inserted_id)
    return event_dict


@router.get("/health", tags=["internal"])   # /analytics/health
def health():
    return {"status": "ok"}


# Register router with the FastAPI app
app.include_router(router)

