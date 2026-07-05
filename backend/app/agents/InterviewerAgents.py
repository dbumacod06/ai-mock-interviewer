from openai import OpenAI
from pydantic_ai import Agent
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from ..repositories import applicant_job_profile_repository
from ..repositories import applicant_cv_repository, applicant_graph_state_repository, applicant_repository
from ..logging_utils import get_method_logger
from ..helpers.prompt_eng_helpers import build_dynamic_system_prompt
from .models import FollowUpDecision, ApplicantInterviewState

load_dotenv(find_dotenv())

method_logger = get_method_logger(__name__)


class InterviewerAgents:
    def __init__(self, model_name: str = "gpt-4o"):
        self.openai_client = OpenAI()

        self.transcription_correction_agent = Agent(
            'openai:gpt-5.4-nano-2026-03-17',
            instructions=(
                "You are an expert audio transcription correction assistant.\n"
                "Your single job is to look at the messy text transcript and correct any misspelled proper nouns, "
                "company names, or technical terms based on the provided reference glossary.\n"
                "Rules:\n"
                "- Only correct words that appear in the glossary above.\n"
                "- Do not guess or invent information.\n"
                "- If a word is not in the glossary, leave it as-is.\n"
                "- Do not rewrite sentences, change grammar, or fix casual slang. Only fix the proper nouns.\n"
                "- Return ONLY the corrected transcript, with no additional commentary."
            ),
            output_type=str
        )


        self.general_interview_agent = Agent(
            'openai:gpt-5.4-nano-2026-03-17',
            instructions=(
                "You are an interview assistant, and your goal is to know more about the applicant. "
                "CRITICAL: You must conduct the interview naturally, asking exactly ONE question at a time. "
                "Never list multiple questions or provide a numbered list. "
                "Wait for the applicant's answer before asking anything else."
            ),
            output_type=str
        )
        

        self.question_generating_agent = Agent(
            'openai:gpt-5.4-nano-2026-03-17',
            instructions=(
                "You are an interview assistant.\n"
                "You are tasked with generating a question that will be asked to a candidate for a given company, and position.\n"
                "The generated question must be concise, 1-3 sentences long, and phrased naturally, similar to how a spoken interview question is constructed."
            ),
            output_type=str
        )


        self.answer_reviewing_agent = Agent(
            'openai:gpt-5.4-nano-2026-03-17',
            instructions=(
                "You are an expert interviewer evaluating a candidate's response. "
                "Evaluate the candidate's latest response. If they didn't actually answer the prompt, "
                "gave a shallow response, or missed critical technical details, set needs_followup to True "
                "and provide a polite, highly specific follow-up question in the reasoning field. "
                "If their answer is standard and acceptable, set needs_followup to False."
            ),
            output_type=FollowUpDecision
        )


        self.inquiry_evaluator_agent = Agent(
            'openai:gpt-5.4-nano-2026-03-17',
            instructions=(
                "You are evaluating if a candidate has more questions for the company. "
                "Return False if the candidate explicitly states they have no more questions or indicates they are ready to conclude the interview. "
                "Return True if they are asking a question, making a statement, or generally engaging."
            ),
            output_type=bool
        )


        self.interview_review_agent = Agent(
            'openai:gpt-4o',
            instructions=(
                "You are an expert interview coach. Your task is to generate a concise, factual suggested response "
                "to an interviewer's question, written from the perspective of the applicant.\n\n"
                "Rules:\n"
                "- Base your response ONLY on the applicant's profile, CV, and job profile provided in the prompt.\n"
                "- Do not fabricate or guess information not present in the provided data.\n"
                "- Write in first person, as if the applicant is speaking.\n"
                "- Keep the response concise (2-4 sentences).\n"
                "- Be specific and reference relevant experience, skills, or achievements from the applicant's background.\n"
                "- Return ONLY the suggested response, with no additional commentary."
            ),
            output_type=str
        )

    
    def transcribe(self, file_path: str, applicant_details, job_profile) -> str:
        transcription_prompt = f"""
            The candidate's first name is {applicant_details.get("first_name")}.
            The candidate's last name is {applicant_details.get("last_name")}.
            The candidate's preferred name is {applicant_details.get("preferred_name")}.
            The candidate is applying for the {job_profile.get("job_title")} position at {job_profile.get("company")}.
            The candidate is currently a/an {applicant_details.get("current_role")} at {applicant_details.get("current_company")}.
            The candidate has previously worked at {applicant_details.get("previous_companies")}
        """
        with open(file_path, "rb") as audio_file:
            response = self.openai_client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                prompt=transcription_prompt,
            )

        return getattr(response, "text", "").strip()

    def _build_glossary(self, applicant_details: dict, cv_data: dict, job_profile: dict) -> str:
        """Build a categorized glossary of proper nouns for transcription correction."""
        names: list[str] = []
        job_titles: list[str] = []
        companies: list[str] = []

        first_name = applicant_details.get("first_name", "")
        last_name = applicant_details.get("last_name", "")
        preferred_name = applicant_details.get("preferred_name", "")
        if first_name:
            names.append(first_name)
        if last_name:
            names.append(last_name)
        if preferred_name:
            names.append(preferred_name)

        previous_companies = applicant_details.get("previous_companies", "")
        if previous_companies:
            if isinstance(previous_companies, str):
                companies.extend([c.strip() for c in previous_companies.split(",") if c.strip()])
            elif isinstance(previous_companies, list):
                companies.extend([c for c in previous_companies if c])

        current_role = applicant_details.get("current_role", "")
        current_company = applicant_details.get("current_company", "")
        if current_role:
            job_titles.append(current_role)
        if current_company:
            companies.append(current_company)

        resume = cv_data.get("resume", cv_data) if cv_data else {}
        cv_current_role = resume.get("current_role", "")
        cv_current_company = resume.get("current_company", "")
        if cv_current_role:
            job_titles.append(cv_current_role)
        if cv_current_company:
            companies.append(cv_current_company)

        past_roles = resume.get("past_roles", [])
        for role in past_roles:
            role_title = role.get("role", "")
            company = role.get("company", "")
            if role_title:
                job_titles.append(role_title)
            if company:
                companies.append(company)


        job_title = job_profile.get("job_title", "")
        company = job_profile.get("company", "")
        if job_title:
            job_titles.append(job_title)
        if company:
            companies.append(company)

        names = sorted(set(names))
        job_titles = sorted(set(job_titles))
        companies = sorted(set(companies))

        lines: list[str] = []
        if names:
            lines.append("Candidate Names:")
            lines.extend(f"- {name}" for name in names)
            lines.append("")
        if job_titles:
            lines.append("Job Titles:")
            lines.extend(f"- {title}" for title in job_titles)
            lines.append("")
        if companies:
            lines.append("Companies:")
            lines.extend(f"- {company}" for company in companies)
            lines.append("")

        return "\n".join(lines)

    async def generate_review_response(self, applicant_details: dict, cv_data: dict, job_profile: dict, interviewer_question: str) -> str:
        method_logger.enter("generate_review_response", applicant_id=applicant_details.get("id", "unknown"))

        resume = cv_data.get("resume", cv_data) if cv_data else {}
        current_role = resume.get("current_role", "")
        current_company = resume.get("current_company", "")
        current_responsibilities = resume.get("current_responsibilities", "")
        past_roles = resume.get("past_roles", [])

        past_roles_str = ""
        for role in past_roles:
            past_roles_str += f"- {role.get('role', '')} at {role.get('company', '')}: {role.get('responsibilities', '')}\n"

        review_prompt = f"""Applicant Profile:
- Name: {applicant_details.get('first_name', '')} {applicant_details.get('last_name', '')}
- Preferred Name: {applicant_details.get('preferred_name', '')}
- Current Role: {applicant_details.get('current_role', '')}
- Current Company: {applicant_details.get('current_company', '')}
- Previous Companies: {applicant_details.get('previous_companies', '')}

CV / Resume:
- Current Role: {current_role}
- Current Company: {current_company}
- Current Responsibilities: {current_responsibilities}
- Past Roles:
{past_roles_str}

Job Profile:
- Position: {job_profile.get('job_title', '')}
- Company: {job_profile.get('company', '')}
- Job Description: {job_profile.get('job_description', '')}
- Company Vision: {job_profile.get('company_vision', '')}
- Company Mission: {job_profile.get('company_mission', '')}
- Additional Context: {job_profile.get('additional_context', '')}

Interviewer's Question:
{interviewer_question}

Based on the applicant's profile, CV, and the job they are applying for above, generate a concise, factual suggested response to the interviewer's question. Write in first person as if you are the applicant."""

        method_logger.agent_invoked("interview_review_agent", prompt=interviewer_question)
        result = await self.interview_review_agent.run(review_prompt)
        method_logger.agent_used("interview_review_agent", response=result.output)
        # method_logger.exit("generate_review_response", result_length=len(result.output))
        return result.output

    async def correct_transcription(self, applicant_details: dict, cv_data: dict, job_profile: dict, transcription: str) -> str:
        """Correct transcription using the glossary."""
        method_logger.enter("correct_transcription", applicant_id=applicant_details.get("id", "unknown"))

        glossary = self._build_glossary(applicant_details, cv_data, job_profile)

        dynamic_instructions = f"""You are an expert audio transcription correction assistant.
Your single job is to look at the messy text transcript and correct any misspelled proper nouns, company names, or technical terms based on the provided reference glossary.

Reference Glossary:
{glossary}

Rules:
- Only correct words that appear in the glossary above.
- Do not guess or invent information.
- If a word is not in the glossary, leave it as-is.
- Do not rewrite sentences, change grammar, or fix casual slang. Only fix the proper nouns.
- Return ONLY the corrected transcript, with no additional commentary.

Transcript:
"""

        method_logger.agent_invoked("transcription_correction_agent", prompt=transcription)
        method_logger.dynamic_string("System prompt: {prompt}", prompt=dynamic_instructions)
        result = await self.transcription_correction_agent.run(transcription, instructions=dynamic_instructions)
        method_logger.agent_used("transcription_correction_agent", response=result.output)
        method_logger.exit("correct_transcription", result=result.output)
        return result.output

    async def run_interview(self, applicant_details: dict, cv_data: dict, job_profile: dict, messages: list, current_phase_name: str) -> str:
        method_logger.enter("run_interview", applicant_id=applicant_details.get("id", "unknown"))

        user_prompt = messages[-1].content
        history_str = self._format_history(messages[-4:])

        dynamic_system_prompt = build_dynamic_system_prompt(
            interview_phase=current_phase_name,
            conversation_hist=history_str,
            applicant_details=applicant_details,
            cv_data=cv_data,
            job_profile=job_profile,
        )
        
        method_logger.dynamic_string("System prompt: {prompt}", prompt=dynamic_system_prompt)
        result = await self.general_interview_agent.run(user_prompt, instructions=dynamic_system_prompt)
        method_logger.exit("run_interview", result=result.output)
        return result.output

    async def review_applicant_answer(self, current_phase_name: str, messages: list, follow_up_count: int) -> FollowUpDecision:
        method_logger.enter("review_applicant_answer")
        latest_message = messages[-1].content if messages else ""
        current_question = messages[-(follow_up_count + 1)].content
        recent_messages = messages[-5:]
        history_str = self._format_history(recent_messages)

        agent_instructions = (
            f"You are an expert interviewer evaluating a candidate's response during the {current_phase_name} phase.\n"
            f"The current primary question is: '{current_question}'\n\n"
            f"Recent conversation history:\n{history_str}\n\n"
            "Evaluate the candidate's latest response in the context of the conversation history above. "
            "If they didn't actually answer the prompt, gave a shallow response, or missed critical technical details, "
            "set needs_followup to True, provide a polite, highly specific reasoning, and generate a concise follow-up question in the followup_question field. "
            "If the candidate explicitly states they have no experience, lack knowledge on the topic, or cannot answer the question, "
            "set needs_followup to False and leave followup_question empty (do not push them further). "
            "If their answer is standard and acceptable, set needs_followup to False and leave followup_question empty."
        )

        method_logger.agent_invoked("answer_reviewing_agent", prompt=latest_message)
        result = await self.answer_reviewing_agent.run(latest_message, instructions=agent_instructions)
        method_logger.agent_used("answer_reviewing_agent", response=result.output)
        # method_logger.exit("review_applicant_answer", needs_followup=result.output.needs_followup)
        return result.output

    async def evaluate_applicant_inquiries(self, latest_message: str) -> bool:
        method_logger.enter("evaluate_applicant_inquiries")

        method_logger.agent_invoked("inquiry_evaluator_agent", prompt=latest_message)
        result = await self.inquiry_evaluator_agent.run(latest_message)
        method_logger.agent_used("inquiry_evaluator_agent", response=result.output)
        # method_logger.exit("evaluate_applicant_inquiries", has_more_questions=result.output)
        return result.output
    
    def _format_history(self, messages: list) -> str:
        history_lines = []
        for msg in messages:
            role = "Candidate" if isinstance(msg, HumanMessage) else "Interviewer"
            history_lines.append(f"{role}: {msg.content}")
        return "\n".join(history_lines)


class _LazyInterviewAgent:
    _instance: "InterviewerAgents | None" = None

    def _get_instance(self) -> "InterviewerAgents":
        if self._instance is None:
            self._instance = InterviewerAgents()
        return self._instance

    # def transcribe(self,file_path: str, applicant_details: dict, job_profile: list[dict]) -> str:
    def transcribe(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        file_path = state.get("saved_audio_path", "")
        job_profile_id = state.get("job_profile_id", "")
        transcribed_text = self._get_instance().transcribe(
            file_path, 
            applicant_repository.get_by_id(state.get("applicant_id")).data, 
            applicant_job_profile_repository.get_by_id(job_profile_id).data
        )
        return {"transcribed_text": transcribed_text}


    async def correct_transcription(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        corrected_text = await self._get_instance().correct_transcription(
            applicant_repository.get_by_id(state.get("applicant_id")).data, 
            applicant_cv_repository.get_by_applicant_and_version(state.get("applicant_id"), state.get("cv_version")).data,
            applicant_job_profile_repository.get_by_id(state.get("job_profile_id")).data,
            state.get("transcribed_text")
        )
        return {"messages": [HumanMessage(content=corrected_text)]}
        


    async def evaluate_and_route(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        interview_phases = state.get("interview_phases", [])
        current_phase_index = state.get("current_phase_index", 0)

        if current_phase_index >= len(interview_phases) - 1:
            return {
                "messages": [AIMessage(content="Thank you for your time. The interview is now complete.")],
                "next_action": None
            }

        current_phase = interview_phases[current_phase_index]
        current_phase_name = current_phase["name"]
        current_phase_questions_asked = state.get("current_phase_questions_asked", 0)
        messages = state.get("messages", [])
        latest_message = messages[-1].content if messages else ""

        if current_phase_name == "applicant_inquiries":
            if current_phase_questions_asked > 0:
                inquiry_result = await self._get_instance().evaluate_applicant_inquiries(latest_message)
                if not inquiry_result:
                    return {
                        "messages": [AIMessage(content="Thank you for your time. The interview is now complete.")],
                        "current_phase_index": current_phase_index + 1,
                        "current_phase_questions_asked": 0,
                        "next_action": "end"
                    }
                return {"next_action": "applicant_inquiries"}
            else:
                return {"next_action": "evaluate_answer"}

        return {"next_action": "evaluate_answer"}

    async def applicant_inquiries_node(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        messages = state.get("messages", [])
        current_phase_index = state.get("current_phase_index", 0)
        current_phase_questions_asked = state.get("current_phase_questions_asked", 0)

        model_response = await self._get_instance().run_interview(
            applicant_repository.get_by_id(state.get("applicant_id")).data,
            applicant_cv_repository.get_by_applicant_and_version(state.get("applicant_id"), state.get("cv_version")).data,
            applicant_job_profile_repository.get_by_id(state.get("job_profile_id")).data,
            messages,
            "applicant_inquiries"
        )

        return {
            "messages": [AIMessage(content=model_response)],
            "current_phase_index": current_phase_index,
            "current_phase_questions_asked": current_phase_questions_asked + 1,
            "follow_up_count": 0,
            "next_action": None
        }

    async def evaluate_answer_node(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        interview_phases = state.get("interview_phases", [])
        current_phase_index = state.get("current_phase_index", 0)
        current_phase = interview_phases[current_phase_index]
        current_phase_name = current_phase["name"]
        follow_up_count = state.get("follow_up_count", 0)

        messages = state.get("messages", [])
        decision = await self._get_instance().review_applicant_answer(current_phase_name, messages, follow_up_count)

        max_followups = current_phase.get("max_followup_questions", 0)
        if decision.needs_followup and follow_up_count < max_followups:
            return {
                "messages": [AIMessage(content=decision.followup_question)],
                "follow_up_count": follow_up_count + 1,
                "next_action": None
            }

        return {"next_action": "generate_response"}

    async def generate_response_node(self, state: ApplicantInterviewState) -> ApplicantInterviewState:
        interview_phases = state.get("interview_phases", [])
        current_phase_index = state.get("current_phase_index", 0)
        current_phase_questions_asked = state.get("current_phase_questions_asked", 0)
        current_phase = interview_phases[current_phase_index]
        current_phase_name = current_phase["name"]

        max_questions = current_phase.get("max_questions", 0)

        if current_phase_questions_asked >= max_questions and max_questions != -1:
            current_phase_index += 1
            current_phase_questions_asked = 0

            if current_phase_index >= len(interview_phases) - 1:
                return {
                    "messages": [AIMessage(content="Thank you for your time. The interview is now complete.")],
                    "current_phase_index": current_phase_index,
                    "next_action": None
                }

            current_phase = interview_phases[current_phase_index]
            current_phase_name = current_phase["name"]

            if current_phase_name == "applicant_inquiries" and current_phase_questions_asked == 0:
                interview_question = "That concludes my questions. Do you have any questions for me about the company or the role?"
                return {
                    "messages": [AIMessage(content=interview_question)],
                    "current_phase_index": current_phase_index,
                    "current_phase_questions_asked": current_phase_questions_asked + 1,
                    "follow_up_count": 0,
                    "next_action": None
                }

        messages = state.get("messages", [])

        model_response = await self._get_instance().run_interview(
            applicant_repository.get_by_id(state.get("applicant_id")).data,
            applicant_cv_repository.get_by_applicant_and_version(state.get("applicant_id"), state.get("cv_version")).data,
            applicant_job_profile_repository.get_by_id(state.get("job_profile_id")).data,
            messages,
            current_phase_name
        )

        return {
            "messages": [AIMessage(content=model_response)],
            "current_phase_index": current_phase_index,
            "current_phase_questions_asked": current_phase_questions_asked + 1,
            "follow_up_count": 0,
            "next_action": None
        }


interviewAgent = _LazyInterviewAgent()
