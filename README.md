# Interview Bot

An AI-powered voice interview platform that conducts automated job interviews using speech-to-text, LLM-driven conversation, and structured interview phases.

## Architecture

- **Backend**: FastAPI service handling interview workflow, transcription, and AI agents
- **Frontend**: React + Vite voice assistant UI
- **Database**: Supabase (PostgreSQL) for applicant data, conversations, and graph state
- **AI**: OpenAI GPT-4o for transcription, interview generation, and answer evaluation

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Supabase project

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp app/.env.template app/.env
   ```
   Edit `app/.env` with your credentials (see [Configuration](#configuration)).

5. Run the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open `http://localhost:5173` in your browser.

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for transcription and AI agents | `sk-proj-...` |
| `SB_PROJECT_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SB_ANON_KEY` | Supabase anonymous key | `eyJhbGci...` |
| `APPLICANT_TABLE` | Supabase table for applicant details | `applicant_details` |
| `APPLICANT_CONVERSATIONS_TABLE` | Table for conversation history | `applicant_conversations` |
| `APPLICANT_CV_TABLE` | Table for applicant CV/resume data | `applicant_cv` |
| `APPLICANT_JOB_PROFILE_TABLE` | Table for job profiles | `applicant_job_profiles` |
| `APPLICANT_SESSIONS_TABLE` | Table for interview sessions | `applicant_sessions` |
| `APPLICANT_GRAPH_STATES_TABLE` | Table for LangGraph state persistence | `applicant_graph_states` |

### Interview Phases

The interview follows a structured flow with configurable phases:

| Phase | Max Questions | Max Follow-ups | Description |
|-------|---------------|----------------|-------------|
| `icebreaker` | 1 | 1 | Casual, non-technical warm-up |
| `preliminary` | 2 | 1 | Introductory screening questions |
| `technical` | 3 | 3 | Technical capability assessment |
| `situational` | 2 | 1 | Hypothetical workplace scenarios |
| `applicant_inquiries` | Unlimited | 0 | Candidate asks questions about role/company |
| `done` | 0 | 0 | Interview complete |

## User Flow

1. **Applicant Registration**: Applicant details and CV are stored in Supabase. A job profile is assigned.

2. **Session Initialization**: A new interview session is created with a LangGraph state machine initialized to the `icebreaker` phase.

3. **Voice Input**: The applicant speaks their response through the frontend UI. Audio is recorded and sent to the backend.

4. **Transcription**: The audio is transcribed using OpenAI's `gpt-4o-transcribe` model, with proper nouns corrected using a glossary built from the applicant's profile.

5. **Interview Workflow** (LangGraph):
   - **`transcriber`**: Converts audio to text
   - **`transcription_corrector`**: Fixes misspelled names, companies, and technical terms
   - **`evaluate_and_route`**: Determines the next action based on interview state
   - **`evaluate_answer_node`**: Reviews the applicant's answer, decides if a follow-up is needed
   - **`generate_response_node`**: Generates the next interview question or handles phase advancement
   - **`applicant_inquiries_node`**: Responds to the applicant's questions about the role/company

6. **Phase Advancement**: The interview progresses through phases based on question counts. If an answer is vague or shallow, a follow-up question is generated (up to the phase's max follow-ups).

7. **Completion**: When all phases are complete or the applicant indicates they have no more questions, the interview ends with a completion message.

## API Endpoints

- `POST /api/transcribe` - Transcribe audio file
- `POST /api/chat` - Process interview turn
- `GET /api/applicants` - List applicants
- `POST /api/applicants` - Create applicant
- `GET /api/applicants/{id}` - Get applicant details
