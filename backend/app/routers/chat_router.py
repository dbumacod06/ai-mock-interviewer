from fastapi import APIRouter, File, Form, UploadFile

from ..logging_utils import get_method_logger
from ..repositories import conversation_repository, applicant_graph_state_repository
from ..services import transcribe_service, interview_review_service

router = APIRouter(prefix="/api", tags=["chat"])
method_logger = get_method_logger(__name__)


@router.get("/conversations/{session_id}")
async def get_conversations(session_id: str) -> dict:
    conversation_response = conversation_repository.get_by_session(session_id)
    messages = getattr(conversation_response, "data", []) or []

    graph_state = applicant_graph_state_repository.get_graph_state(session_id)
    phases = graph_state.get("interview_phases", [])
    current_phase_index = graph_state.get("current_phase_index", 0)
    interview_phase = ""
    if phases and current_phase_index < len(phases):
        interview_phase = phases[current_phase_index].get("name", "")

    return {
        "messages": messages,
        "interview_phase": interview_phase,
    }


@router.get("/interview-review/{session_id}")
async def get_interview_review(session_id: str) -> dict:
    method_logger.enter("get_interview_review", session_id=session_id)
    result = await interview_review_service.review_interview(session_id)
    # method_logger.exit("get_interview_review", pair_count=len(result.get("review_pairs", [])))
    return result


@router.post("/transcribe")
async def transcribe_and_respond(
    applicant_id: str = Form(...),
    session_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict[str, str]:
    applicant_id = applicant_id.strip()
    session_id = session_id.strip()
    method_logger.enter("transcribe_and_respond", applicant_id=applicant_id, session_id=session_id, filename=file.filename)
    result = await transcribe_service.transcribe_and_respond(file, applicant_id, session_id)
    method_logger.exit("transcribe_and_respond", result={"transcribed_length": len(result.get("transcribed_text", "")), "response_length": len(result.get("model_response", ""))})
    return result
