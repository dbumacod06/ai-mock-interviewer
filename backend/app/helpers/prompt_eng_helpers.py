def build_dynamic_system_prompt(
    interview_phase: str,
    conversation_hist: str = '',
    applicant_details: dict = {},
    cv_data: dict = {},
    job_profile: dict = {},
) -> str:
    """Build a dynamic system prompt personalized for the interview phase and applicant context."""

    dynamic_system_prompt = ""
    preferred_name = applicant_details.get("preferred_name", "Not Provided")
    first_name = applicant_details.get("first_name", "Not Provided")
    last_name = applicant_details.get("last_name", "Not Provided")

    resume = cv_data.get("resume", {}) if cv_data else {}
    current_role = resume.get("current_role", "Not Provided")
    current_company = resume.get("current_company", "Not Provided")
    current_responsibilities = resume.get("current_responsibilities", "Not Provided")
    job_vision = job_profile.get("company_vision", "Not Provided")
    job_mission = job_profile.get("company_mission", "Not Provided")
    additional_context = job_profile.get("additional_context", "Not Provided")

    past_roles = resume.get("past_roles", [])
    past_roles_str = "None listed"
    if past_roles:
        past_roles_str = "\n".join(
            f"- {role.get('role', '')} at {role.get('company', '')}: {role.get('responsibilities', '')}"
            for role in past_roles
        )

    applied_job_title = job_profile.get("job_title", "Not Provided")
    applied_company = job_profile.get("company", "Not Provided")
    applied_job_description = job_profile.get("job_description", "Not Provided")

    
    if interview_phase == "icebreaker":
        dynamic_system_prompt = (
            f"Generate a single unnumbered, entirely non-technical icebreaker question for an applicant named {preferred_name} who is based in Manila, Philippines. "
            "The question must be concise, lighthearted, casual, and focused purely on their day, well-being, or location (e.g., asking about the weather, how they are feeling, or local life). "
            "Do NOT mention any job titles, work, skills, AI, or professional background whatsoever."
        )


    if interview_phase == "applicant_inquiries":
        goal_prompt = (
            "Your goal is to answer the applicant's questions about the company and the role. "
            "Use the job profile context. If you don't know the exact answer, provide a plausible, "
            "professional response or ask a clarifying question. "
            "Always end by asking if they have any other questions."
        )

        dynamic_system_prompt = f"""{goal_prompt}

CRITICAL CONSTRAINTS:
1. Keep your response concise, conversational, and limited to 1-3 sentences.
2. Make it sound like a natural, spoken interview.

Applicant Detail:
- Preferred Name: {preferred_name}

Job Details:
- Title: {applied_job_title}
- Description: {applied_job_description}

Company Details:
- Name: {applied_company}
- Vision: {job_vision}
- Mission: {job_mission}
- Additional Information: {additional_context}

Conversation History:
{conversation_hist}

Address the applicant by their preferred name , and tailor answers based on the job and company details."""


    if interview_phase == "preliminary":
        goal_prompt = (
            "Your goal is to ask preliminary, non-technical interview questions for an applicant",     
            "The questions must be introductory screening questions focused on behavioral, or logistical aspects (e.g., 'Tell me about yourself', 'Why are you looking to leave your current role?', 'What interested you about our company?', or 'What are your career goals?')",
            "Do not ask about specific coding languages, system architectures, frameworks, tools, or hard technical skills related to the role",
            )

        dynamic_system_prompt = f"""{goal_prompt}

CRITICAL CONSTRAINTS:
1. Ask EXACTLY ONE question at a time. Do NOT provide a list of questions.
2. Keep your response concise, conversational, and limited to 1-3 sentences.
3. Make it sound like a natural, spoken interview.
4. The generated question must be a completely fresh, standalone problem statement. Do not ask a follow-up question based on previous answers or ongoing dialogue.

Applicant Context:
- Preferred Name: {preferred_name}
- Current Role: {current_role}
- Current Company: {current_company}
- Current Responsibilities: {current_responsibilities}
- Past Roles:
{past_roles_str}

Job Applied for:
- Title: {applied_job_title}
- Description: {applied_job_description}

Company Details:
- Company: {applied_company}
- Vision: {job_vision}
- Mission: {job_mission}
- Additional Information: {additional_context}


Conversation History:
{conversation_hist}

Use this context to personalize the interview. Address the applicant by their preferred name if available, and tailor questions based on their background and experience."""
    
    
    if interview_phase == "technical":
        goal_prompt = (
            "Your goal is to generate exactly ONE high-quality, targeted technical interview question for a candidate, assessing their advanced technical capabilities.",
            )

        dynamic_system_prompt = f"""{goal_prompt}

CRITICAL CONSTRAINTS:
1. Ask EXACTLY ONE question at a time. Do NOT provide a list of questions.
2. Keep your response concise, conversational, and limited to 1-3 sentences.
3. Make it sound like a natural, spoken interview.
4. The generated question must be a completely fresh, standalone problem statement. Do not ask a follow-up question based on previous answers or ongoing dialogue.

Applicant Context:
- Preferred Name: {preferred_name}
- Current Role: {current_role}
- Current Company: {current_company}
- Current Responsibilities: {current_responsibilities}
- Past Roles:
{past_roles_str}

Job Applied for:
- Title: {applied_job_title}
- Company: {applied_company}
- Description: {applied_job_description}

Conversation History:
{conversation_hist}

Use this context to personalize the interview. Address the applicant by their preferred name if available, and tailor questions based on the skills and experience relevant to the role they are applying for."""


        

    if interview_phase in ["situational"]:

        goal_prompt = (
            "Combine the candidate's professional domain with the company's business context to construct a hypothetical, high-stakes workplace situation. The scenario should mimic a real problem they would face in this specific role at this specific company."
            "The question must actively gauge core interpersonal and cultural competencies, specifically: how they handle difficult cross-functional situations, manage stakeholder conflict, navigate missing requirements/tight deadlines, or champion cultural values under pressure."
        )

        dynamic_system_prompt = f"""{goal_prompt}

CRITICAL CONSTRAINTS:
1. Ask EXACTLY ONE question at a time. Do NOT provide a list of questions.
2. Keep your response concise, conversational, and limited to 1-3 sentences.
3. Make it sound like a natural, spoken interview.
4. The generated question must be a completely fresh, standalone problem statement. Do not ask a follow-up question based on previous answers or ongoing dialogue.

Applicant Context:
- Preferred Name: {preferred_name}
- Current Role: {current_role}
- Current Company: {current_company}
- Current Responsibilities: {current_responsibilities}
- Past Roles:
{past_roles_str}

Job Applied for:
- Title: {applied_job_title}
- Description: {applied_job_description}

Company Details:
- Company: {applied_company}
- Vision: {job_vision}
- Mission: {job_mission}
- Additional Information: {additional_context}

Use this context to personalize the interview. Address the applicant by their preferred name if available, and tailor questions based on the skills and experience relevant to the role they are applying for."""

    return dynamic_system_prompt
