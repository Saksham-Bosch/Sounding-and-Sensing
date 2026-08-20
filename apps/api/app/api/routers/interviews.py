import uuid
from datetime import datetime, timezone
from pathlib import Path
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.integrations.moderation.client import check_content_safety, is_safe_url
from app.integrations.parsers.document_parser import parse_document
from app.integrations.stt.client import process_media_file
from app.repositories.excel_adapter import ExcelDatabase
from app.schemas.interviews import AnswerCreate, AnswerResponse, InterviewSession

router = APIRouter()
db = ExcelDatabase()
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "local" / "uploads"


@router.post("/start", response_model=InterviewSession, status_code=201)
async def start_interview(event_id: str, questionnaire_id: str, participant_role: str = "General"):
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
        "participant_role": participant_role,
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
    sessions = db.get_all_records("InterviewSessions")
    session = next((s for s in sessions if s.get("session_id") == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    normalized_text = ""
    if answer.input_type == "text":
        normalized_text = answer.content
    elif answer.input_type == "url":
        if not is_safe_url(answer.content):
            raise HTTPException(status_code=400, detail="URL blocked due to SSRF/security policy.")

        # Scrape the URL using existing document parser
        normalized_text = await parse_document(answer.content, "url")

        if not await check_content_safety(normalized_text):
            raise HTTPException(status_code=400, detail="Submission rejected: Content violates safety policies.")
    else:
        normalized_text = f"[Pending processing for {answer.input_type}]"

    answer_dict = {
        "id": f"ans-{uuid.uuid4().hex[:8]}",
        "session_id": session_id,
        "question_id": answer.question_id,
        "input_type": answer.input_type,
        "content": answer.content,
        "normalized_text": normalized_text,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    db.save_record("InterviewAnswers", answer_dict)
    session["current_question_position"] = int(session.get("current_question_position", 1)) + 1
    db.save_record("InterviewSessions", session)
    return AnswerResponse(**answer_dict)


@router.post("/{session_id}/answer/file", response_model=AnswerResponse, status_code=201)
async def submit_file_answer(
    session_id: str,
    question_id: str = Form(...),
    file: UploadFile = File(...),
):
    sessions = db.get_all_records("InterviewSessions")
    session = next((s for s in sessions if s.get("session_id") == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_extension = Path(file.filename).suffix
    local_file_path = UPLOAD_DIR / f"file-{uuid.uuid4().hex[:8]}{file_extension}"

    with local_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    mime_type = file.content_type or ""

    try:
        if file_extension.lower() in [".mp3", ".wav", ".mp4", ".mov", ".avi", ".m4a"]:
            normalized_text = await process_media_file(local_file_path)
        else:
            normalized_text = await parse_document(local_file_path, mime_type)
    finally:
        # Always delete the original uploaded file after processing is complete
        if local_file_path.exists():
            local_file_path.unlink()

    answer_dict = {
        "id": f"ans-{uuid.uuid4().hex[:8]}",
        "session_id": session_id,
        "question_id": question_id,
        "input_type": "file",
        "content": str(file.filename),
        "normalized_text": normalized_text,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    db.save_record("InterviewAnswers", answer_dict)
    session["current_question_position"] = int(session.get("current_question_position", 1)) + 1
    db.save_record("InterviewSessions", session)
    return AnswerResponse(**answer_dict)
