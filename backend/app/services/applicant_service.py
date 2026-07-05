import secrets
import string
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from ..logging_utils import get_method_logger
from ..repositories import ApplicantRepository, applicant_repository

method_logger = get_method_logger(__name__)


class ApplicantSubmission(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(validation_alias=AliasChoices("first_name", "firstName"))
    last_name: str = Field(validation_alias=AliasChoices("last_name", "lastName"))
    preferred_name: str = Field(validation_alias=AliasChoices("preferred_name", "preferredName"))
    current_role: str = Field(default="", validation_alias=AliasChoices("current_role", "currentRole"))
    current_company: str = Field(default="", validation_alias=AliasChoices("current_company", "currentCompany"))
    previous_companies: str = Field(default="", validation_alias=AliasChoices("previous_companies", "previousCompanies"))

    @field_validator("first_name", "last_name", "preferred_name", mode="before")
    @classmethod
    def title_case_required_strings(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        value = value.strip()
        if not value:
            raise ValueError("Value is required")

        return value.title()

    @field_validator("current_role", "current_company", mode="before")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str:
        if value is None:
            return ""

        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        return value.strip()

    @field_validator("previous_companies", mode="before")
    @classmethod
    def clean_previous_companies(cls, value: str | None) -> str:
        if value is None:
            return ""

        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        return value.strip()


class ApplicantUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(default="", validation_alias=AliasChoices("first_name", "firstName"))
    last_name: str = Field(default="", validation_alias=AliasChoices("last_name", "lastName"))
    preferred_name: str = Field(default="", validation_alias=AliasChoices("preferred_name", "preferredName"))
    current_role: str = Field(default="", validation_alias=AliasChoices("current_role", "currentRole"))
    current_company: str = Field(default="", validation_alias=AliasChoices("current_company", "currentCompany"))
    previous_companies: str = Field(default="", validation_alias=AliasChoices("previous_companies", "previousCompanies"))

    @field_validator("first_name", "last_name", "preferred_name", mode="before")
    @classmethod
    def title_case_required_strings(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        value = value.strip()
        if not value:
            raise ValueError("Value is required")

        return value.title()

    @field_validator("current_role", "current_company", mode="before")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str:
        if value is None:
            return ""

        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        return value.strip()

    @field_validator("previous_companies", mode="before")
    @classmethod
    def clean_previous_companies(cls, value: str | None) -> str:
        if value is None:
            return ""

        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        return value.strip()


class ApplicantService:
    def __init__(self, repository: ApplicantRepository = applicant_repository) -> None:
        self.repository = repository

    def save_submission(self, applicant: ApplicantSubmission) -> dict[str, Any]:
        method_logger.enter("save_submission", first_name=applicant.first_name, last_name=applicant.last_name)
        applicant_id = self._generate_applicant_id()
        response = self.repository.insert(
            {
                "id": applicant_id,
                "first_name": applicant.first_name,
                "last_name": applicant.last_name,
                "preferred_name": applicant.preferred_name,
                "current_role": applicant.current_role,
                "current_company": applicant.current_company,
                "previous_companies": applicant.previous_companies,
            }
        )
        applicant_row = response.data[0] if getattr(response, "data", None) else {"id": applicant_id}

        result = {
            "applicant_id": applicant_row.get("id", applicant_id),
            "applicant": self._format_applicant(applicant_row),
        }
        method_logger.exit("save_submission", result=result)
        return result

    def update_submission(self, applicant_id: str, applicant: ApplicantUpdate) -> dict[str, Any]:
        method_logger.enter("update_submission", applicant_id=applicant_id)
        applicant_id = applicant_id.strip()
        update_data = {}
        if applicant.first_name:
            update_data["first_name"] = applicant.first_name
        if applicant.last_name:
            update_data["last_name"] = applicant.last_name
        if applicant.preferred_name:
            update_data["preferred_name"] = applicant.preferred_name
        if applicant.current_role is not None:
            update_data["current_role"] = applicant.current_role
        if applicant.current_company is not None:
            update_data["current_company"] = applicant.current_company
        if applicant.previous_companies is not None:
            update_data["previous_companies"] = applicant.previous_companies

        response = self.repository.update(applicant_id, update_data)
        applicant_row = response.data[0] if getattr(response, "data", None) else {"id": applicant_id}

        result = {
            "applicant_id": applicant_row.get("id", applicant_id),
            "applicant": self._format_applicant(applicant_row),
        }
        method_logger.exit("update_submission", result=result)
        return result

    def get_submission(self, applicant_id: str) -> dict[str, Any] | None:
        method_logger.enter("get_submission", applicant_id=applicant_id)
        applicant_id = applicant_id.strip()
        response = self.repository.get_by_id(applicant_id)
        if not getattr(response, "data", None):
            method_logger.exit("get_submission", result=None)
            return None

        applicant_row = response.data
        result = {
            "applicant_id": applicant_row.get("id", applicant_id),
            "applicant": self._format_applicant(applicant_row),
        }
        method_logger.exit("get_submission", result=result)
        return result

    def _generate_applicant_id(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return f"app_usr_{''.join(secrets.choice(alphabet) for _ in range(7))}"

    def _format_applicant(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "applicantId": row.get("id", ""),
            "firstName": row.get("first_name", ""),
            "lastName": row.get("last_name", ""),
            "preferredName": row.get("preferred_name", ""),
            "currentRole": row.get("current_role", ""),
            "currentCompany": row.get("current_company", ""),
            "previousCompanies": row.get("previous_companies", ""),
        }


applicant_service = ApplicantService()
