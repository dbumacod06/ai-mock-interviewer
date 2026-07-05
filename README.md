# Interview Bot (In-Progress)

A **stateless**, AI-powered voice interview platform that conducts fully automated job interviews from start to finish. The system combines OpenAI's speech-to-text for accurate transcription with LLM-driven agents that manage natural, context-aware conversation — all orchestrated through a LangGraph state machine that enforces a structured multi-phase interview flow.

**Stateless by design**: The backend holds no in-memory session state between requests. Every API call is self-contained: the full interview context (conversation history, phase tracking, question counts, follow-up status) is persisted in Supabase and reconstructed on each turn via LangGraph's graph execution. This architecture delivers:
- **Zero session affinity** — any server instance can handle any request
- **Horizontal scalability** — spin up additional instances without coordination
- **Crash resilience** — server restarts never lose interview progress; state rehydrates from the database
- **Clean concurrency** — multiple interviews run independently with no shared mutable state

## Architecture

- **Backend**: FastAPI service with LangGraph-driven interview workflow, transcription pipeline, and specialist AI agents
- **Frontend**: React + Vite voice assistant UI with real-time microphone recording, audio visualization, and Markdown-rendered responses
- **Database**: Supabase (PostgreSQL) for applicant data, conversations, CVs, job profiles, sessions, and LangGraph state persistence
- **AI**: OpenAI GPT-4o for transcription, interview question generation, answer evaluation, and applicant inquiry responses

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

## Database Schema

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for full table definitions, relationships, and the LangGraph state structure.
