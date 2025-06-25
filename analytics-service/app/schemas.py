from pydantic import BaseModel

class EventCreate(BaseModel):
    service: str
    event_type: str
    metadata: dict

class EventOut(EventCreate):
    id: str
