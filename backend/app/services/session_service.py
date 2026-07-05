import uuid
from typing import Any
from ..helpers.graph_state_helpers import initialize_graph_state
from ..repositories import applicant_cv_repository, ApplicantCvRepository
from ..logging_utils import get_method_logger
from ..repositories import ApplicantJobProfileRepository, applicant_job_profile_repository
from ..repositories.session_repository import SessionRepository, session_repository
from ..repositories.applicant_graph_state_repository import ApplicantGraphStateRepository, applicant_graph_state_repository


method_logger = get_method_logger(__name__)


class SessionService:
    def __init__(
        self,
        repository: SessionRepository = session_repository,
        job_profile_repository: ApplicantJobProfileRepository = applicant_job_profile_repository,
        cv_repository: ApplicantCvRepository = applicant_cv_repository,
    ) -> None:
        self.repository = repository
        self.job_profile_repository = job_profile_repository
        self.cv_repository = cv_repository

    async def create_session(
        self, applicant_id: str, cv_version: int, job_profile_id: str
    ) -> dict[str, Any]:
        method_logger.enter("create_session", applicant_id=applicant_id, cv_version=cv_version, job_profile_id=job_profile_id)
        new_session_id = str(uuid.uuid4())
        response = self.repository.insert(
            {
                "applicant_id": applicant_id,
                "cv_version": cv_version,
                "job_profile_id": job_profile_id,
                "session_id": new_session_id,
                "is_done": False,
            }
        )
        row = response.data[0] if getattr(response, "data", None) else {}
        if row:
            await initialize_graph_state(applicant_id, new_session_id, job_profile_id, cv_version)
        result = {
            "session_id": new_session_id,
            "applicant_id": row.get("applicant_id", applicant_id),
            "cv_version": cv_version,
            "job_profile_id": job_profile_id,
            "created_at": row.get("created_at", ""),
        }
        method_logger.exit("create_session", result=result)
        return result

    def get_applicant_sessions(self, applicant_id: str) -> list[dict[str, Any]]:
        method_logger.enter("get_applicant_sessions", applicant_id=applicant_id)
        applicant_id = applicant_id.strip()
        response = self.repository.get_by_applicant_id(applicant_id)
        if not getattr(response, "data", None):
            method_logger.exit("get_applicant_sessions", result=[])
            return []

        sessions = []
        for row in response.data:
            job_profile = self._get_job_profile_summary(row.get("job_profile_id", ""))
            sessions.append(
                {
                    "session_id": row.get("session_id", ""),
                    "applicant_id": row.get("applicant_id", ""),
                    "cv_version": row.get("cv_version", 0),
                    "job_profile": job_profile,
                    "created_at": row.get("created_at", ""),
                    "is_done": row.get("is_done", False),
                }
            )

        method_logger.exit("get_applicant_sessions", result=len(sessions))
        return sessions

    def delete_session(self, session_id: str) -> dict[str, Any]:
        method_logger.enter("delete_session", session_id=session_id)
        response = self.repository.delete(session_id)
        if getattr(response, "data", None):
            result = {"success": True, "session_id": session_id}
        else:
            result = {"success": False, "session_id": session_id}
        method_logger.exit("delete_session", result=result)
        return result

    def _get_job_profile_summary(self, job_profile_id: str) -> dict[str, str]:
        if not job_profile_id:
            return {"job_title": "", "company": ""}

        response = self.job_profile_repository.get_by_id(job_profile_id)
        if not getattr(response, "data", None):
            return {"job_title": "", "company": ""}

        row = response.data
        return {
            "job_title": row.get("job_title", ""),
            "company": row.get("company", ""),
        }


session_service = SessionService()
