from fastapi import HTTPException

from ..agents.InterviewerAgents import interviewAgent
from ..logging_utils import get_method_logger
from ..repositories import (
    applicant_cv_repository,
    applicant_graph_state_repository,
    applicant_job_profile_repository,
    applicant_repository,
    conversation_repository,
    session_repository,
)

method_logger = get_method_logger(__name__)


class InterviewReviewService:
    async def review_interview(self, session_id: str) -> dict:
        method_logger.enter("review_interview", session_id=session_id)

        session_response = session_repository.get_by_session_id(session_id)
        session_data = getattr(session_response, "data", None)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_data[0] if isinstance(session_data, list) else session_data
        applicant_id = session.get("applicant_id", "")

        graph_state = applicant_graph_state_repository.get_graph_state(session_id)
        phases = graph_state.get("interview_phases", [])
        current_phase_index = graph_state.get("current_phase_index", 0)
        current_phase = ""
        if phases and current_phase_index < len(phases):
            current_phase = phases[current_phase_index].get("name", "")

        if current_phase != "done":
            raise HTTPException(status_code=400, detail="Interview session is not yet complete")

        conversation_response = conversation_repository.get_by_session(session_id)
        conversations = getattr(conversation_response, "data", []) or []

        assistant_messages: list[str] = []
        for msg in conversations:
            if msg.get("role") == "assistant":
                content = (msg.get("content") or "").strip()
                if content and "Thank you for your time" not in content:
                    assistant_messages.append(content)

        if not assistant_messages:
            method_logger.exit("review_interview", result="no assistant messages found")
            return {"review_pairs": []}

        applicant_data = applicant_repository.get_by_id(applicant_id).data or {}
        cv_data = applicant_cv_repository.get_by_applicant_and_version(
            applicant_id, graph_state.get("cv_version", "")
        ).data or {}
        job_profile_data = applicant_job_profile_repository.get_by_id(
            graph_state.get("job_profile_id", "")
        ).data or {}

        review_pairs = []
        for question in assistant_messages:
            method_logger.dynamic_string("Generating review for question: {question}", question=question[:80])
            try:
                suggested_response = await interviewAgent.generate_review_response(
                    applicant_data, cv_data, job_profile_data, question
                )
            except Exception as e:
                method_logger.dynamic_string("Error generating review response: {error}", error=str(e))
                suggested_response = "Could not generate a suggested response for this question."
            review_pairs.append({
                "interviewer_question": question,
                "suggested_response": suggested_response,
            })

        # method_logger.exit("review_interview", pair_count=len(review_pairs))
        return {"review_pairs": review_pairs}


interview_review_service = InterviewReviewService()
