import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.questionnaires import QuestionnaireResponse, QuestionnaireCreate
from app.repositories.excel_adapter import ExcelDatabase
from app.integrations.mra.client import generate_questionnaire_from_mra

router = APIRouter()
db = ExcelDatabase()

@router.post("/generate", response_model=QuestionnaireResponse, status_code=201)
async def generate_questionnaire(request: QuestionnaireCreate):
    # 1. Fetch the event to get context (using the mock DB)
    events = db.get_all_records("Events")
    event = next((e for e in events if e.get("id") == request.event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # 2. Extract a research topic from the event title/description
    topic = f"{event.get('title', '')} - {event.get('description', '')}"
    
    # 3. Call the external MRA Agent
    try:
        generated_json = await generate_questionnaire_from_mra(topic)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MRA Generation failed: {str(e)}")
        
    # 4. Enforce IDs and prepare for DB
    questionnaire_id = f"qnr-{uuid.uuid4().hex[:8]}"
    generated_json["questionnaire_id"] = questionnaire_id
    generated_json["event_id"] = request.event_id
    generated_json["schema_version"] = "1.0"
    
    # Separate questions for relational storage (flattening for Excel)
    questions = generated_json.pop("questions", [])
    for idx, q in enumerate(questions):
        q["id"] = f"qst-{uuid.uuid4().hex[:8]}"
        q["questionnaire_id"] = questionnaire_id
        db.save_record("GeneratedQuestions", q)
        
    # Save the base questionnaire record
    db.save_record("Questionnaires", generated_json)
    
    # Re-attach questions for the API response
    generated_json["questions"] = questions
    return QuestionnaireResponse(**generated_json)

@router.get("/", response_model=List[QuestionnaireResponse])
async def list_questionnaires():
    records = db.get_all_records("Questionnaires")
    all_questions = db.get_all_records("GeneratedQuestions")
    
    # Reconstruct the nested structure
    for record in records:
        record["questions"] = [q for q in all_questions if q.get("questionnaire_id") == record["questionnaire_id"]]
        
    return [QuestionnaireResponse(**record) for record in records]