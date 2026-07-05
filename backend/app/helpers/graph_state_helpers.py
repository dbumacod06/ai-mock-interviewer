from ..helpers.prompt_eng_helpers import build_dynamic_system_prompt

from ..agents.InterviewerAgents import interviewAgent
from ..config import INTERVIEW_CONFIG
from langchain_core.messages import HumanMessage, AIMessage
from ..repositories import (
    applicant_graph_state_repository,
    conversation_repository,
    applicant_repository
)


async def prepare_graph_state_input(saved_audio_path: str, session_id: str) -> dict:
    graph_state_input = applicant_graph_state_repository.get_graph_state(session_id)
    graph_state_input["saved_audio_path"] = saved_audio_path
    graph_state_input.setdefault("next_action", None)

    interview_phases = graph_state_input.get("interview_phases", [])
    current_phase_index = graph_state_input.get("current_phase_index", 0)

    if interview_phases[current_phase_index]["name"] == "done":
        # Interview already done — placeholder guard
        return graph_state_input

    graph_state_input["messages"] = []
    conversation_history = conversation_repository.get_by_session(session_id, 10).data or []
    for row in conversation_history:
        if row.get('role') == 'user':
            graph_state_input["messages"].append(HumanMessage(content=row['content']))
        elif row.get('role') == 'assistant':
            graph_state_input["messages"].append(AIMessage(content=row['content']))

    return graph_state_input


async def initialize_graph_state(applicant_id: str, session_id: str, job_profile_id: str, cv_version: str) -> dict:
    
    dynamic_system_prompt = build_dynamic_system_prompt(
        interview_phase="icebreaker",
        applicant_details=applicant_repository.get_by_id(applicant_id).data
    )
    result = await interviewAgent._get_instance().question_generating_agent.run(
        "Greet the applicant and initiate the interview",
        instructions=dynamic_system_prompt
    )
    graph_state = {
        "applicant_id": applicant_id,
        "session_id": session_id,
        "job_profile_id": job_profile_id,
        "cv_version": cv_version,
        "interview_phases": INTERVIEW_CONFIG["phases"],
        "current_phase_index": 0,
        "current_phase_questions_asked": 1,
        "follow_up_count": 0,
        "next_action": None,
        "messages": []
    }
    conversation_repository.insert(
        {
            "applicant_id": applicant_id,
            "session_id": session_id,
            "role": "assistant",
            "content": result.output
        }
    )
    applicant_graph_state_repository.save_graph_state(session_id, graph_state)
    return graph_state
