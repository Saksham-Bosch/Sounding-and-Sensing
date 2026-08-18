import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.events import EventCreate, EventResponse
from app.repositories.excel_adapter import ExcelDatabase

router = APIRouter()
db = ExcelDatabase()

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(event: EventCreate):
    # Convert request schema to dictionary
    event_dict = event.model_dump()
    
    # Generate system-controlled fields
    event_dict["id"] = f"evt-{uuid.uuid4().hex[:8]}"
    event_dict["created_at"] = datetime.now(timezone.utc)
    event_dict["organization_id"] = "org-local-poc" # Hardcoded for Phase 1 POC
    
    # Save to the Excel Mock Database
    try:
        db.save_record(sheet_name="Events", record_dict=event_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    return EventResponse(**event_dict)

@router.get("/", response_model=List[EventResponse])
async def list_events():
    # Retrieve all records from the Excel mock database
    try:
        records = db.get_all_records(sheet_name="Events")
        return [EventResponse(**record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
