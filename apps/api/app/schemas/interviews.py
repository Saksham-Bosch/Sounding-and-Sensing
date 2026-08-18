from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnswerCreate(BaseModel):
    question_id: str
    input_type: str = Field(..., description="e.g., text, audio, pdf, etc.")
    content: Optional[str] = Field(None, description="Raw text or reference to asset")
    
class AnswerResponse(AnswerCreate):
    id: str
    normalized_text: str
    processed_at: datetime

class InterviewSession(BaseModel):
    session_id: str
    event_id: str
    questionnaire_id: str
    status: str = Field(default="IN_PROGRESS", description="IN_PROGRESS or COMPLETED")
    current_question_position: int = 1
