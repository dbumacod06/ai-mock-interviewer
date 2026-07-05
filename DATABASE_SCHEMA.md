# Database Schema

All tables are hosted on Supabase (PostgreSQL). Table names are configurable via environment variables — the names below reflect the default configuration.

## Tables

### `applicant_details`

Stores core applicant identity and employment summary.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `varchar` | **PK** |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` |
| `first_name` | `varchar` | `NOT NULL` |
| `last_name` | `varchar` | `NOT NULL` |
| `preferred_name` | `varchar` | `NOT NULL` |
| `current_role` | `varchar` | `NOT NULL` |
| `current_company` | `varchar` | `NOT NULL` |
| `previous_companies` | `varchar` | `NOT NULL` |

### `applicant_cv`

Stores applicant CV/resume data as JSONB, with versioning support.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `uuid` | **PK**, default `gen_random_uuid()` |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` |
| `applicant_id` | `varchar` | `NOT NULL`, FK → `applicant_details(id)` |
| `resume` | `jsonb` | `NOT NULL` |
| `version` | `integer` | `NOT NULL` |

**Resume JSONB structure:**
```json
{
  "current_role": "string",
  "current_company": "string",
  "current_responsibilities": "string",
  "past_roles": [
    {
      "role": "string",
      "company": "string",
      "responsibilities": "string"
    }
  ]
}
```

### `applicant_job_profiles`

Stores job profiles (position, company, description) that an applicant is interviewing for.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `uuid` | **PK**, default `gen_random_uuid()` |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` |
| `applicant_id` | `varchar` | `NOT NULL`, FK → `applicant_details(id)` |
| `job_title` | `varchar` | `NOT NULL` |
| `company` | `varchar` | `NOT NULL` |
| `job_description` | `varchar` | `NOT NULL` |
| `company_vision` | `varchar` | nullable |
| `company_mission` | `varchar` | nullable |
| `additional_context` | `varchar` | nullable |

### `applicant_sessions`

Tracks interview sessions, linking an applicant to a specific CV version and job profile.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `uuid` | **PK**, default `gen_random_uuid()` |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` |
| `applicant_id` | `varchar` | `NOT NULL`, FK → `applicant_details(id)` |
| `cv_version` | `integer` | `NOT NULL` |
| `job_profile_id` | `uuid` | `NOT NULL`, FK → `applicant_job_profiles(id)` |
| `session_id` | `varchar` | `NOT NULL`, **UNIQUE** |
| `is_done` | `boolean` | `NOT NULL` |

### `applicant_conversations`

Stores the turn-by-turn conversation history for each interview session.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `uuid` | **PK**, default `gen_random_uuid()` |
| `created_at` | `timestamptz` | `NOT NULL`, default `now()` |
| `session_id` | `varchar` | `NOT NULL`, FK → `applicant_sessions(session_id)` |
| `applicant_id` | `varchar` | `NOT NULL`, FK → `applicant_details(id)` |
| `role` | `varchar` | `NOT NULL` (`"user"` or `"assistant"`) |
| `content` | `text` | `NOT NULL` |

**Index:** `idx_conversations_session_created` on `(session_id, created_at DESC)`

### `applicant_graph_states`

Persists LangGraph state for each active interview session, enabling stateless request handling.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `uuid` | **PK**, default `gen_random_uuid()` |
| `session_id` | `varchar` | `NOT NULL`, **UNIQUE**, FK → `applicant_sessions(session_id)` `ON DELETE CASCADE` |
| `graph_state` | `jsonb` | `NOT NULL`, default `'{}'` |
| `updated_at` | `timestamptz` | `NOT NULL`, default `now()` |

## Relationships

```
applicant_details (1) ──┬── (N) applicant_cv
                        ├── (N) applicant_job_profiles
                        ├── (N) applicant_sessions
                        └── (N) applicant_conversations

applicant_sessions (1) ──┬── (1) applicant_graph_states (CASCADE DELETE)
                         └── (N) applicant_conversations

applicant_job_profiles (1) ── (N) applicant_sessions
```

## Graph State Structure

The `graph_state` JSONB in `applicant_graph_states` follows the `ApplicantInterviewState` schema:

```json
{
  "messages": [
    { "role": "user|assistant", "content": "string" }
  ],
  "interview_question": "string | null",
  "interview_phases": [
    { "name": "string", "max_questions": "int", "max_followup_questions": "int" }
  ],
  "current_phase_index": "int",
  "current_phase_questions_asked": "int",
  "session_id": "string",
  "saved_audio_path": "string",
  "cv_version": "int",
  "job_profile_id": "string",
  "applicant_id": "string",
  "transcribed_text": "string | null",
  "follow_up_count": "int",
  "next_action": "string | null"
}
```
