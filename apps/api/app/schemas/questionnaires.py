from pydantic import BaseModel, Field
from typing import List, Optional

class Question(BaseModel):
    id: str
    position: int
    text: str
    type: str = Field(default="OPEN_TEXT")
    required: bool = True
    allowed_input_types: List[str] = Field(default_factory=lambda: ["text", "audio", "image", "pdf", "docx", "pptx", "xlsx", "video", "url"])
    guidance: Optional[str] = None
    branch_rules: list = Field(default_factory=list)

class QuestionnaireBase(BaseModel):
    title: str = Field(default="Customized Event Interview")
    questions: List[Question]

class QuestionnaireCreate(QuestionnaireBase):
    event_id: str

class QuestionnaireResponse(QuestionnaireBase):
    questionnaire_id: str
    event_id: str
    schema_version: str = "1.0"
