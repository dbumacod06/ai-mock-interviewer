from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from ..logging_utils import get_method_logger
from ..repositories.applicant_cv_repository import ApplicantCvRepository, applicant_cv_repository

method_logger = get_method_logger(__name__)


class PastRole(BaseModel):
    role: str
    company: str
    responsibilities: str


class ApplicantCvSubmission(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    applicant_id: str = Field(validation_alias=AliasChoices("applicant_id", "applicantId"))
    current_role: str = Field(validation_alias=AliasChoices("current_role", "currentRole"))
    current_company: str = Field(validation_alias=AliasChoices("current_company", "currentCompany"))
    current_responsibilities: str = Field(
        validation_alias=AliasChoices("current_responsibilities", "currentResponsibilities")
    )
    past_roles: list[PastRole] = Field(validation_alias=AliasChoices("past_roles", "pastRoles"))


class ApplicantCvService:
    def __init__(self, repository: ApplicantCvRepository = applicant_cv_repository) -> None:
        self.repository = repository

    def save_submission(self, cv: ApplicantCvSubmission) -> dict[str, Any]:
        method_logger.enter("save_submission", applicant_id=cv.applicant_id, current_role=cv.current_role)
        resume_data = {
            "current_role": cv.current_role,
            "current_company": cv.current_company,
            "current_responsibilities": cv.current_responsibilities,
            "past_roles": [role.model_dump() for role in cv.past_roles],
        }

        latest_version = self.repository.get_latest_version(cv.applicant_id)
        new_version = latest_version + 1 if latest_version else 1

        response = self.repository.insert(
            {
                "applicant_id": cv.applicant_id,
                "resume": resume_data,
                "version": new_version,
            }
        )
        row = response.data[0] if getattr(response, "data", None) else {"applicant_id": cv.applicant_id}

        result = {
            "applicant_id": row.get("applicant_id", cv.applicant_id),
            "cv": self._format_cv(row),
        }
        method_logger.dynamic_string("CV saved: {applicant_id} version {version}", applicant_id=cv.applicant_id, version=new_version)
        method_logger.exit("save_submission", result=result)
        return result

    def get_submission(self, applicant_id: str) -> dict[str, Any] | None:
        method_logger.enter("get_submission", applicant_id=applicant_id)
        response = self.repository.get_by_applicant_id(applicant_id)
        if not getattr(response, "data", None):
            method_logger.exit("get_submission", result=None)
            return None

        row = response.data[0]
        result = {
            "applicant_id": row.get("applicant_id", applicant_id),
            "cv": self._format_cv(row),
        }
        method_logger.exit("get_submission", result=result)
        return result

    def get_submission_by_version(self, applicant_id: str, version: int) -> dict[str, Any] | None:
        method_logger.enter("get_submission_by_version", applicant_id=applicant_id, version=version)
        response = self.repository.get_by_applicant_and_version(applicant_id, version)
        if not getattr(response, "data", None):
            method_logger.exit("get_submission_by_version", result=None)
            return None

        row = response.data[0]
        result = {
            "applicant_id": row.get("applicant_id", applicant_id),
            "cv": self._format_cv(row),
        }
        method_logger.exit("get_submission_by_version", result=result)
        return result

    def get_all_versions(self, applicant_id: str) -> list[dict[str, Any]]:
        method_logger.enter("get_all_versions", applicant_id=applicant_id)
        response = self.repository.get_all_by_applicant_id(applicant_id)
        if not getattr(response, "data", None):
            method_logger.exit("get_all_versions", result=[])
            return []

        result = [
            {
                "applicant_id": row.get("applicant_id", applicant_id),
                "cv": self._format_cv(row),
            }
            for row in response.data
        ]
        method_logger.exit("get_all_versions", result=len(result))
        return result

    def _format_cv(self, row: dict[str, Any]) -> dict[str, Any]:
        resume = row.get("resume", {}) or {}
        past_roles = resume.get("past_roles", []) or []
        return {
            "applicantId": row.get("applicant_id", ""),
            "version": row.get("version", 1),
            "currentRole": resume.get("current_role", ""),
            "currentCompany": resume.get("current_company", ""),
            "currentResponsibilities": resume.get("current_responsibilities", ""),
            "pastRoles": past_roles if isinstance(past_roles, list) else [],
        }


applicant_cv_service = ApplicantCvService()
