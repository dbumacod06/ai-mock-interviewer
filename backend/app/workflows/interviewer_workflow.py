from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph, add_messages
from ..agents.models import ApplicantInterviewState
from ..agents.InterviewerAgents import interviewAgent
from ..repositories import applicant_graph_state_repository


interview_workflow = StateGraph(ApplicantInterviewState)
interview_workflow.add_node("transcriber", interviewAgent.transcribe)
interview_workflow.add_node("transcription_corrector", interviewAgent.correct_transcription)
interview_workflow.add_node("evaluate_and_route", interviewAgent.evaluate_and_route)
interview_workflow.add_node("evaluate_answer_node", interviewAgent.evaluate_answer_node)
interview_workflow.add_node("applicant_inquiries_node", interviewAgent.applicant_inquiries_node)
interview_workflow.add_node("generate_response_node", interviewAgent.generate_response_node)

interview_workflow.add_edge(START, "transcriber")
interview_workflow.add_edge("transcriber", "transcription_corrector")
interview_workflow.add_edge("transcription_corrector", "evaluate_and_route")

interview_workflow.add_conditional_edges(
    "evaluate_and_route",
    lambda state: state.get("next_action"),
    {
        "end": END,
        "applicant_inquiries": "applicant_inquiries_node",
        "evaluate_answer": "evaluate_answer_node"
    }
)

interview_workflow.add_conditional_edges(
    "evaluate_answer_node",
    lambda state: state.get("next_action"),
    {
        "generate_response": "generate_response_node",
        None: END
    }
)

interview_workflow.add_edge("applicant_inquiries_node", END)
interview_workflow.add_edge("generate_response_node", END)

interviewer_wf = interview_workflow.compile()
