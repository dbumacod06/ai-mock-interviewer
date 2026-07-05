from typing import Any, List, Optional

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class ApplicantDetails(BaseModel):
    first_name: Optional[str] = Field(
        default="",
        description="The user's first name."
    )
    last_name: Optional[str] = Field(
        default="",
        description="The user's last name."
    )
    preferred_name: Optional[str] = Field(
        default="",
        description="The user's explicitly given nickname."
    )
    previous_companies: Optional[List[str]] = Field(
        default=[],
        description="List of all the companies the user has worked for."
    )


class FollowUpDecision(BaseModel):
    needs_followup: bool = Field(
        description="True if the candidate's answer was vague, superficial, skipped the prompt, or requires immediate clarification. False if it was sufficient."
    )
    reasoning: str = Field(
        description="Brief internal justification for why a follow-up is or isn't needed based on the interview context."
    )
    followup_question: str = Field(
        default="",
        description="A concise follow-up question to ask the candidate if needs_followup is True. Empty string if no follow-up is needed."
    )


class ReviewPair(BaseModel):
    interviewer_question: str = Field(
        description="The original question asked by the interviewer."
    )
    suggested_response: str = Field(
        description="A concise, factual suggested response based on the applicant's profile and CV."
    )


class ApplicantInterviewState(MessagesState):
    interview_question: Optional[str] = None
    interview_phases: list[dict[str, Any]]
    current_phase_index: int
    current_phase_questions_asked: int = 0
    session_id: str
    saved_audio_path: str
    cv_version: int
    job_profile_id: str
    applicant_id: str
    transcribed_text: Optional[str]
    follow_up_count: int
    next_action: Optional[str] = None
