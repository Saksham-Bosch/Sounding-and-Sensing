from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class EventBase(BaseModel):
    title: str = Field(..., description="Name of the event")
    description: Optional[str] = Field(None, description="Basic event details")
    standard_answers: Dict[str, Any] = Field(default_factory=dict, description="Answers to the standard context questionnaire")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: str
    created_at: datetime
    organization_id: str
