import asyncio
import os
from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.graph.message import StateGraph, add_messages
from langchain_core.messages import SystemMessage, HumanMessage

from ..workflows.interviewer_workflow import interviewer_wf
from ..agents.InterviewerAgents import interviewAgent
from ..helpers.audio_helpers import save_uploaded_audio_file, transcribe_audio_file
from ..helpers.graph_state_helpers import prepare_graph_state_input
from ..logging_utils import get_method_logger
from ..repositories import (
    ApplicantRepository,
    ApplicantCvRepository,
    ApplicantJobProfileRepository,
    SessionRepository,
    ConversationRepository,
    ApplicantGraphStateRepository,
    applicant_cv_repository,
    applicant_job_profile_repository,
    applicant_repository,
    conversation_repository,
    applicant_graph_state_repository,
    session_repository
)

load_dotenv()
method_logger = get_method_logger(__name__)




class TranscribeService:
    def __init__(
        self,
        repository: ApplicantRepository = applicant_repository,
        cv_repository: ApplicantCvRepository = applicant_cv_repository,
        job_profile_repository: ApplicantJobProfileRepository = applicant_job_profile_repository,
        conversation_repo: ConversationRepository = conversation_repository,
        session_repo: SessionRepository = session_repository,
    ) -> None:
        self.repository = repository
        self.cv_repository = cv_repository
        self.job_profile_repository = job_profile_repository
        self.conversation_repo = conversation_repo
        self.session_repo = session_repo

    async def transcribe_and_respond(self, file: UploadFile, applicant_id: str, session_id: str) -> dict[str, str]:
        if not applicant_id or not session_id:
            raise HTTPException(status_code=400, detail="Applicant ID and Session ID are required")
        method_logger.enter("transcribe_and_respond", applicant_id=applicant_id, session_id=session_id)
        
        applicant_response = self.repository.get_by_id(applicant_id)
        if not getattr(applicant_response, "data", None):
            raise HTTPException(status_code=404, detail="Applicant record not found")


        session_check = self.session_repo.get_by_session_id(session_id)
        if not getattr(session_check, "data", None):
            raise HTTPException(status_code=404, detail="Session not found")

        saved_audio_path = save_uploaded_audio_file(file)
        method_logger.dynamic_string("Audio file saved: {path}", path=saved_audio_path)


        graph_state_input = await prepare_graph_state_input(saved_audio_path, session_id)
        workflow_result = await interviewer_wf.ainvoke(graph_state_input)

        applicant_graph_state_repository.save_graph_state(session_id, workflow_result)

        messages = workflow_result.get("messages", [])
        if not messages:
            method_logger.dynamic_string("WARNING: No messages returned from workflow for session={session_id}", session_id=session_id)
        elif len(messages) < 2:
            method_logger.dynamic_string("WARNING: Only {count} message(s) returned from workflow for session={session_id}. Expected at least 2 (user + assistant).", count=len(messages), session_id=session_id)
        else:
            # Insert user message
            try:
                user_message_content = messages[-2].content
                user_insert_data = {
                    "applicant_id": applicant_id,
                    "session_id": session_id,
                    "role": "user",
                    "content": user_message_content,
                }
                user_insert_result = self.conversation_repo.insert(user_insert_data)
                method_logger.dynamic_string("User conversation inserted successfully. Response: {result}", result=getattr(user_insert_result, "data", "no data"))
            except Exception as e:
                method_logger.dynamic_string("ERROR: Failed to insert user conversation for session={session_id}: {error}", session_id=session_id, error=str(e))

            # Insert assistant message
            try:
                assistant_message_content = messages[-1].content
                assistant_insert_data = {
                    "applicant_id": applicant_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "content": assistant_message_content,
                }
                assistant_insert_result = self.conversation_repo.insert(assistant_insert_data)
                method_logger.dynamic_string("Assistant conversation inserted successfully. Response: {result}", result=getattr(assistant_insert_result, "data", "no data"))
            except Exception as e:
                method_logger.dynamic_string("ERROR: Failed to insert assistant conversation for session={session_id}: {error}", session_id=session_id, error=str(e))

        method_logger.dynamic_string("Conversation saved: {applicant_id} session={session_id}", applicant_id=applicant_id, session_id=session_id)

        phases = workflow_result.get("interview_phases", [])
        current_phase_index = workflow_result.get("current_phase_index", 0)
        interview_phase = ""
        if phases and current_phase_index < len(phases):
            interview_phase = phases[current_phase_index].get("name", "")

        if interview_phase == "done":
            try:
                self.session_repo.update(session_id, {"is_done": True})
                method_logger.dynamic_string("Session marked as done: {session_id}", session_id=session_id)
            except Exception as e:
                method_logger.dynamic_string("ERROR: Failed to mark session as done: {error}", error=str(e))

        result = {
            "applicant_id": applicant_id,
            "session_id": session_id,
            "transcribed_text": workflow_result.get("transcribed_text"),
            "corrected_text": workflow_result.get("messages", [])[-2].content if workflow_result.get("messages") else "",
            "model_response": workflow_result.get("messages", [])[-1].content if workflow_result.get("messages") else "",
            "interview_phase": interview_phase,
            "filename": os.path.basename(saved_audio_path),
            "saved_path": saved_audio_path,
        }
        method_logger.exit("transcribe_and_respond", result={"transcribed_length": len(workflow_result.get("transcribed_text", "")), "response_length": len(workflow_result.get("messages", [])[-1].content if workflow_result.get("messages") else "")})
        return result


transcribe_service = TranscribeService()
