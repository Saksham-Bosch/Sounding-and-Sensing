import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.repositories.excel_adapter import ExcelDatabase
from app.schemas.interviews import AnswerCreate, AnswerResponse, InterviewSession

router = APIRouter()
db = ExcelDatabase()


@router.post("/start", response_model=InterviewSession, status_code=201)
async def start_interview(event_id: str, questionnaire_id: str):
    """Initializes a new interview session for a given questionnaire."""
    # Verify questionnaire exists
    questionnaires = db.get_all_records("Questionnaires")
    if not any(q.get("questionnaire_id") == questionnaire_id for q in questionnaires):
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    session_id = f"ses-{uuid.uuid4().hex[:8]}"

    session_data = {
        "session_id": session_id,
        "event_id": event_id,
        "questionnaire_id": questionnaire_id,
        "status": "IN_PROGRESS",
        "current_question_position": 1,
    }

    db.save_record("InterviewSessions", session_data)
    return InterviewSession(**session_data)


@router.get("/{session_id}/next-question")
async def get_next_question(session_id: str):
    """Retrieves the current question based on session position."""
    sessions = db.get_all_records("InterviewSessions")
    session = next((s for s in sessions if s.get("session_id") == session_id), None)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("status") == "COMPLETED":
        return {"message": "Interview complete", "completed": True}

    # Fetch questions for this questionnaire
    questions = db.get_all_records("GeneratedQuestions")
    qnr_questions = [q for q in questions if q.get("questionnaire_id") == session.get("questionnaire_id")]

    # Sort by position and find the current one
    qnr_questions.sort(key=lambda x: int(x.get("position", 0)))
    current_pos = int(session.get("current_question_position", 1))

    # Find the question that matches the current position
    current_q = next((q for q in qnr_questions if int(q.get("position", 0)) == current_pos), None)

    if not current_q:
        # If no question exists at this position, we reached the end
        session["status"] = "COMPLETED"
        db.save_record("InterviewSessions", session)  # Excel adapter 'replace' mode appends in our mock, but this is fine for POC
        return {"message": "Interview complete", "completed": True}

    return {"completed": False, "question": current_q}


@router.post("/{session_id}/answer", response_model=AnswerResponse, status_code=201)
async def submit_answer(session_id: str, answer: AnswerCreate):
    """Saves a text answer and advances the session position."""
    sessions = db.get_all_records("InterviewSessions")
    session = next((s for s in sessions if s.get("session_id") == session_id), None)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Process the text answer
    answer_id = f"ans-{uuid.uuid4().hex[:8]}"
    processed_at = datetime.now(timezone.utc)

    answer_dict = answer.model_dump()
    answer_dict["id"] = answer_id
    answer_dict["session_id"] = session_id
    answer_dict["normalized_text"] = answer.content if answer.input_type == "text" else f"[Pending processing for {answer.input_type}]"
    answer_dict["processed_at"] = processed_at

    # Save the answer
    db.save_record("InterviewAnswers", answer_dict)

    # Advance the session position
    session["current_question_position"] = int(session.get("current_question_position", 1)) + 1
    # Hack for the POC Excel mock: we append the updated session. In a real DB we would UPDATE.
    db.save_record("InterviewSessions", session)

    return AnswerResponse(**answer_dict)
