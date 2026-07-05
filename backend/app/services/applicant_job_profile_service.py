from typing import Any
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from ..logging_utils import get_method_logger
from ..repositories import ApplicantJobProfileRepository, applicant_job_profile_repository

method_logger = get_method_logger(__name__)


class ApplicantJobProfileSubmission(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    applicant_id: str = Field(validation_alias=AliasChoices("applicant_id", "applicantId"))
    job_title: str = Field(validation_alias=AliasChoices("job_title", "jobTitle"))
    company: str = Field(validation_alias=AliasChoices("company", "company"))
    job_description: str = Field(validation_alias=AliasChoices("job_description", "jobDescription"))
    company_vision: str = Field(validation_alias=AliasChoices("company_vision", "companyVision"))
    company_mission: str = Field(validation_alias=AliasChoices("company_mission", "companyMission"))
    additional_context: str = Field(
        default="", validation_alias=AliasChoices("additional_context", "additionalContext")
    )


class ApplicantJobProfileUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_title: str = Field(validation_alias=AliasChoices("job_title", "jobTitle"))
    company: str = Field(validation_alias=AliasChoices("company", "company"))
    job_description: str = Field(validation_alias=AliasChoices("job_description", "jobDescription"))
    company_vision: str = Field(validation_alias=AliasChoices("company_vision", "companyVision"))
    company_mission: str = Field(validation_alias=AliasChoices("company_mission", "companyMission"))
    additional_context: str = Field(
        default="", validation_alias=AliasChoices("additional_context", "additionalContext")
    )


class ApplicantJobProfileService:
    def __init__(
        self, repository: ApplicantJobProfileRepository = applicant_job_profile_repository
    ) -> None:
        self.repository = repository

    def save_submission(self, profile: ApplicantJobProfileSubmission) -> dict[str, Any]:
        method_logger.enter("save_submission", applicant_id=profile.applicant_id, job_title=profile.job_title)
        response = self.repository.insert(
            {
                "applicant_id": profile.applicant_id,
                "job_title": profile.job_title,
                "company": profile.company,
                "job_description": profile.job_description,
                "company_vision": profile.company_vision,
                "company_mission": profile.company_mission,
                "additional_context": profile.additional_context,
            }
        )
        row = response.data[0] if getattr(response, "data", None) else {"applicant_id": profile.applicant_id}

        result = {
            "applicant_id": row.get("applicant_id", profile.applicant_id),
            "profile": self._format_profile(row),
        }
        method_logger.exit("save_submission", result=result)
        return result

    def update_submission(self, profile_id: str, profile: ApplicantJobProfileUpdate) -> dict[str, Any]:
        method_logger.enter("update_submission", profile_id=profile_id)
        response = self.repository.update(
            profile_id,
            {
                "job_title": profile.job_title,
                "company": profile.company,
                "job_description": profile.job_description,
                "company_vision": profile.company_vision,
                "company_mission": profile.company_mission,
                "additional_context": profile.additional_context,
            },
        )
        row = response.data[0] if getattr(response, "data", None) else {}
        result = {
            "profile_id": row.get("id", profile_id),
            "applicant_id": row.get("applicant_id", ""),
            "profile": self._format_profile(row),
        }
        method_logger.exit("update_submission", result=result)
        return result

    def get_submissions(self, applicant_id: str) -> list[dict[str, Any]]:
        method_logger.enter("get_submissions", applicant_id=applicant_id)
        applicant_id = applicant_id.strip()
        response = self.repository.get_by_applicant_id(applicant_id)
        if not getattr(response, "data", None):
            method_logger.exit("get_submissions", result=[])
            return []

        result = [
            {
                "profile_id": row.get("id", ""),
                "applicant_id": row.get("applicant_id", ""),
                "profile": self._format_profile(row),
            }
            for row in response.data
        ]
        method_logger.exit("get_submissions", result=len(result))
        return result

    def _format_profile(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "profileId": row.get("id", ""),
            "applicantId": row.get("applicant_id", ""),
            "jobTitle": row.get("job_title", ""),
            "company": row.get("company", ""),
            "jobDescription": row.get("job_description", ""),
            "companyVision": row.get("company_vision", ""),
            "companyMission": row.get("company_mission", ""),
            "additionalContext": row.get("additional_context", ""),
        }


applicant_job_profile_service = ApplicantJobProfileService()
