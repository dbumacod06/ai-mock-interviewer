import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_requires_audio_file(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = [{"id": applicant_id}]
            return MockResponse()

    class MockSessionRepo:
        def get_by_session_id(self, session_id):
            class MockResponse:
                data = [{"id": "sess_1", "session_id": session_id}]
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "session_repo", MockSessionRepo())

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "app_usr_123", "session_id": "test_session"},
        files={"file": ("sample.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Only recorded audio files are supported" in response.json()["detail"]


def test_transcribe_missing_applicant_id(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = None
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "missing_user", "session_id": "test_session"},
        files={"file": ("audio.mp3", b"audio content", "audio/mpeg")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Applicant record not found"


def test_transcribe_missing_session_id(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = [{"id": applicant_id}]
            return MockResponse()

    class MockSessionRepo:
        def get_by_session_id(self, session_id):
            class MockResponse:
                data = None
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "session_repo", MockSessionRepo())

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "app_usr_123", "session_id": "invalid_session"},
        files={"file": ("audio.mp3", b"audio content", "audio/mpeg")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_transcribe_session_id_required(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = [{"id": applicant_id}]
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "app_usr_123"},
        files={"file": ("audio.mp3", b"audio content", "audio/mpeg")},
    )

    assert response.status_code == 422


def test_transcribe_missing_cv_data(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = [{"id": applicant_id}]
            return MockResponse()

    class MockSessionRepo:
        def get_by_session_id(self, session_id):
            class MockResponse:
                data = [{"id": "sess_1", "session_id": session_id}]
            return MockResponse()

    class MockCvRepo:
        def get_by_applicant_id(self, applicant_id):
            class MockResponse:
                data = None
            return MockResponse()

    class MockJobProfileRepo:
        def get_by_applicant_id(self, applicant_id):
            class MockResponse:
                data = [{"job_title": "AI Engineer", "company": "TechCorp"}]
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "session_repo", MockSessionRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "cv_repository", MockCvRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "job_profile_repository", MockJobProfileRepo())
    transcribe_service_module = sys.modules["app.services.transcribe_service"]
    monkeypatch.setattr(transcribe_service_module, "transcribe_audio_file", lambda fp, applicant: "test transcription")

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "app_usr_123", "session_id": "test_session"},
        files={"file": ("audio.mp3", b"audio content", "audio/mpeg")},
    )

    assert response.status_code == 400
    assert "CV data is required" in response.json()["detail"]


def test_transcribe_missing_job_profile(monkeypatch):
    chat_router_module = sys.modules["app.routers.chat_router"]

    class MockApplicantRepo:
        def get_by_id(self, applicant_id, columns="*"):
            class MockResponse:
                data = [{"id": applicant_id}]
            return MockResponse()

    class MockSessionRepo:
        def get_by_session_id(self, session_id):
            class MockResponse:
                data = [{"id": "sess_1", "session_id": session_id}]
            return MockResponse()

    class MockCvRepo:
        def get_by_applicant_id(self, applicant_id):
            class MockResponse:
                data = [{"resume": {"current_role": "AI Engineer", "current_company": "TechCorp"}}]
            return MockResponse()

    class MockJobProfileRepo:
        def get_by_applicant_id(self, applicant_id):
            class MockResponse:
                data = None
            return MockResponse()

    monkeypatch.setattr(chat_router_module.transcribe_service, "repository", MockApplicantRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "session_repo", MockSessionRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "cv_repository", MockCvRepo())
    monkeypatch.setattr(chat_router_module.transcribe_service, "job_profile_repository", MockJobProfileRepo())
    transcribe_service_module = sys.modules["app.services.transcribe_service"]
    monkeypatch.setattr(transcribe_service_module, "transcribe_audio_file", lambda fp, applicant: "test transcription")

    response = client.post(
        "/api/transcribe",
        data={"applicant_id": "app_usr_123", "session_id": "test_session"},
        files={"file": ("audio.mp3", b"audio content", "audio/mpeg")},
    )

    assert response.status_code == 400
    assert "job profile is required" in response.json()["detail"]


def test_applicant_cv_versions(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantCvService:
        def get_all_versions(self, applicant_id: str) -> list:
            return [
                {
                    "applicant_id": applicant_id,
                    "cv": {
                        "applicantId": applicant_id,
                        "version": 2,
                        "currentRole": "Senior Engineer",
                        "currentCompany": "TechCorp",
                        "currentResponsibilities": "Leading team",
                        "pastRoles": [],
                    },
                },
                {
                    "applicant_id": applicant_id,
                    "cv": {
                        "applicantId": applicant_id,
                        "version": 1,
                        "currentRole": "Engineer",
                        "currentCompany": "OldCo",
                        "currentResponsibilities": "Building models",
                        "pastRoles": [],
                    },
                },
            ]

    monkeypatch.setattr(applicant_router_module, "applicant_cv_service", MockApplicantCvService())

    response = client.get("/api/applicant-cv/app_usr_123/versions")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["cv"]["version"] == 2
    assert response.json()[1]["cv"]["version"] == 1


def test_create_session(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockSessionService:
        async def create_session(self, applicant_id: str, cv_version: int, job_profile_id: str) -> dict:
            return {
                "session_id": "test-session-123",
                "applicant_id": applicant_id,
                "cv_version": cv_version,
                "job_profile_id": job_profile_id,
                "created_at": "2024-01-01T00:00:00Z",
            }

    monkeypatch.setattr(applicant_router_module, "session_service", MockSessionService())

    response = client.post(
        "/api/sessions",
        json={
            "applicant_id": "app_usr_123",
            "cv_version": 2,
            "job_profile_id": "prof_123",
        },
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == "test-session-123"
    assert response.json()["cv_version"] == 2


def test_get_applicant_sessions(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockSessionService:
        def get_applicant_sessions(self, applicant_id: str) -> list:
            return [
                {
                    "session_id": "sess_123",
                    "applicant_id": applicant_id,
                    "cv_version": 2,
                    "job_profile": {"job_title": "AI Engineer", "company": "TechCorp"},
                    "created_at": "2024-01-01T00:00:00Z",
                    "is_done": False,
                }
            ]

    monkeypatch.setattr(applicant_router_module, "session_service", MockSessionService())

    response = client.get("/api/applicant-sessions/app_usr_123")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["session_id"] == "sess_123"
    assert response.json()[0]["cv_version"] == 2
    assert response.json()[0]["job_profile"]["job_title"] == "AI Engineer"


def test_delete_session(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockSessionService:
        def delete_session(self, session_id: str) -> dict:
            return {"success": True, "session_id": session_id}

    monkeypatch.setattr(applicant_router_module, "session_service", MockSessionService())

    response = client.delete("/api/sessions/sess_123")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["session_id"] == "sess_123"


def test_applicant_lookup_returns_record(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantService:
        def get_submission(self, applicant_id: str) -> dict:
            return {
                "applicant_id": applicant_id,
                "applicant": {
                    "applicantId": applicant_id,
                    "firstName": "Ada",
                    "lastName": "Lovelace",
                    "preferredName": "Ada",
                    "currentRole": "AI Engineer",
                    "currentCompany": "TechCorp",
                    "previousCompanies": "OldCo",
                },
            }

    monkeypatch.setattr(applicant_router_module, "applicant_service", MockApplicantService())

    response = client.get("/api/applicants/app_usr_123")

    assert response.status_code == 200
    assert response.json()["applicant_id"] == "app_usr_123"
    assert response.json()["applicant"]["firstName"] == "Ada"
    assert response.json()["applicant"]["currentRole"] == "AI Engineer"


def test_applicant_lookup_returns_404(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantService:
        def get_submission(self, applicant_id: str) -> None:
            return None

    monkeypatch.setattr(applicant_router_module, "applicant_service", MockApplicantService())

    response = client.get("/api/applicants/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Applicant record not found"


def test_applicant_save_accepts_camel_case_payload(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantService:
        def save_submission(self, payload) -> dict:
            return {
                "applicant_id": "app_usr_abc",
                "applicant": {
                    "applicantId": "app_usr_abc",
                    "firstName": payload.first_name,
                    "lastName": payload.last_name,
                    "preferredName": payload.preferred_name,
                    "currentRole": payload.current_role,
                    "currentCompany": payload.current_company,
                    "previousCompanies": payload.previous_companies,
                },
            }

    monkeypatch.setattr(applicant_router_module, "applicant_service", MockApplicantService())

    response = client.post(
        "/api/applicants",
        json={
            "firstName": "ada",
            "lastName": "lovelace",
            "preferredName": "  aDa  ",
            "currentRole": "AI Engineer",
            "currentCompany": "TechCorp",
            "previousCompanies": "OldCo, DataCorp",
        },
    )

    assert response.status_code == 200
    assert response.json()["applicant_id"] == "app_usr_abc"
    assert response.json()["applicant"]["firstName"] == "Ada"
    assert response.json()["applicant"]["preferredName"] == "Ada"
    assert response.json()["applicant"]["currentRole"] == "AI Engineer"
    assert response.json()["applicant"]["previousCompanies"] == "OldCo, DataCorp"


def test_applicant_update(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantService:
        def update_submission(self, applicant_id: str, payload) -> dict:
            return {
                "applicant_id": applicant_id,
                "applicant": {
                    "applicantId": applicant_id,
                    "firstName": payload.first_name,
                    "lastName": payload.last_name,
                    "preferredName": payload.preferred_name,
                    "currentRole": payload.current_role,
                    "currentCompany": payload.current_company,
                    "previousCompanies": payload.previous_companies,
                },
            }

    monkeypatch.setattr(applicant_router_module, "applicant_service", MockApplicantService())

    response = client.put(
        "/api/applicants/app_usr_123",
        json={
            "firstName": "Ada",
            "lastName": "Lovelace",
            "preferredName": "Ada",
            "currentRole": "AI Engineer",
            "currentCompany": "TechCorp",
            "previousCompanies": "OldCo",
        },
    )

    assert response.status_code == 200
    assert response.json()["applicant_id"] == "app_usr_123"
    assert response.json()["applicant"]["firstName"] == "Ada"
    assert response.json()["applicant"]["currentRole"] == "AI Engineer"


def test_applicant_documents_upload_accepts_supported_files():
    response = client.post(
        "/api/applicant-documents",
        data={"applicant_id": "app_usr_123"},
        files={
            "resume_file": (
                "resume.docx",
                b"resume content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            "job_description_file": ("job_description.txt", b"job description", "text/plain"),
        },
    )

    assert response.status_code == 200
    assert response.json()["applicant_id"] == "app_usr_123"
    assert response.json()["resume_file"]["filename"] == "resume.docx"
    assert response.json()["job_description_file"]["filename"] == "job_description.txt"


def test_applicant_cv_save_and_get(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantCvService:
        def save_submission(self, payload) -> dict:
            return {
                "applicant_id": payload.applicant_id,
                "cv": {
                    "applicantId": payload.applicant_id,
                    "currentRole": payload.current_role,
                    "currentCompany": payload.current_company,
                    "currentResponsibilities": payload.current_responsibilities,
                    "pastRoles": [role.model_dump() for role in payload.past_roles],
                },
            }

        def get_submission(self, applicant_id: str) -> dict:
            return {
                "applicant_id": applicant_id,
                "cv": {
                    "applicantId": applicant_id,
                    "currentRole": "AI Engineer",
                    "currentCompany": "TechCorp",
                    "currentResponsibilities": "Building models",
                    "pastRoles": [{"role": "Data Scientist", "company": "OldCo", "responsibilities": "Analysis"}],
                },
            }

    monkeypatch.setattr(applicant_router_module, "applicant_cv_service", MockApplicantCvService())

    response = client.post(
        "/api/applicant-cv",
        json={
            "applicantId": "app_usr_123",
            "currentRole": "AI Engineer",
            "currentCompany": "TechCorp",
            "currentResponsibilities": "Building models",
            "pastRoles": [{"role": "Data Scientist", "company": "OldCo", "responsibilities": "Analysis"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["applicant_id"] == "app_usr_123"
    assert response.json()["cv"]["currentRole"] == "AI Engineer"
    assert response.json()["cv"]["currentCompany"] == "TechCorp"

    response = client.get("/api/applicant-cv/app_usr_123")
    assert response.status_code == 200
    assert response.json()["cv"]["currentRole"] == "AI Engineer"
    assert response.json()["cv"]["currentCompany"] == "TechCorp"


def test_applicant_job_profile_save_and_get(monkeypatch):
    applicant_router_module = sys.modules["app.routers.applicant_router"]

    class MockApplicantJobProfileService:
        def save_submission(self, payload) -> dict:
            return {
                "applicant_id": payload.applicant_id,
                "profile": {
                    "profileId": "prof_123",
                    "applicantId": payload.applicant_id,
                    "jobTitle": payload.job_title,
                    "company": payload.company,
                    "jobDescription": payload.job_description,
                    "companyVision": payload.company_vision,
                    "companyMission": payload.company_mission,
                    "additionalContext": payload.additional_context,
                },
            }

        def get_submissions(self, applicant_id: str) -> list:
            return [
                {
                    "profile_id": "prof_123",
                    "applicant_id": applicant_id,
                    "profile": {
                        "profileId": "prof_123",
                        "applicantId": applicant_id,
                        "jobTitle": "AI Engineer",
                        "company": "TechCorp",
                        "jobDescription": "Build AI systems",
                        "companyVision": "",
                        "companyMission": "",
                        "additionalContext": "",
                    },
                }
            ]

    monkeypatch.setattr(applicant_router_module, "applicant_job_profile_service", MockApplicantJobProfileService())

    response = client.post(
        "/api/applicant-job-profiles",
        json={
            "applicantId": "app_usr_123",
            "jobTitle": "AI Engineer",
            "company": "TechCorp",
            "jobDescription": "Build AI systems",
            "companyVision": "To build the future",
            "companyMission": "To innovate",
            "additionalContext": "",
        },
    )

    assert response.status_code == 200
    assert response.json()["profile"]["jobTitle"] == "AI Engineer"
    assert response.json()["profile"]["companyVision"] == "To build the future"

    response = client.get("/api/applicant-job-profiles/app_usr_123")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["profile"]["jobTitle"] == "AI Engineer"
