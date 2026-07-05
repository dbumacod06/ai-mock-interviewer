from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ..logging_utils import get_logger, get_method_logger
from ..services import (
    ApplicantCvSubmission,
    ApplicantJobProfileSubmission,
    ApplicantJobProfileUpdate,
    ApplicantSubmission,
    ApplicantUpdate,
    applicant_cv_service,
    applicant_job_profile_service,
    applicant_service,
    document_service,
    session_service,
)

logger = get_logger(__name__)
method_logger = get_method_logger(__name__)

router = APIRouter(prefix="/api", tags=["applicants"])


class CreateSessionRequest(BaseModel):
    applicant_id: str
    cv_version: int
    job_profile_id: str


@router.post("/applicant-documents")
async def upload_applicant_documents(
    applicant_id: str = Form(...),
    resume_file: UploadFile = File(...),
    job_description_file: UploadFile = File(...),
) -> dict[str, object]:
    method_logger.enter("upload_applicant_documents", applicant_id=applicant_id)
    result = await document_service.upload_applicant_documents(
        applicant_id,
        resume_file,
        job_description_file,
    )
    method_logger.exit("upload_applicant_documents", result=result)
    return result


@router.post("/applicants")
def save_applicant(payload: ApplicantSubmission) -> dict[str, Any]:
    method_logger.enter("save_applicant", first_name=payload.first_name, last_name=payload.last_name)
    result = applicant_service.save_submission(payload)
    method_logger.dynamic_string("Applicant created: {applicant_id}", applicant_id=result["applicant_id"])
    method_logger.exit("save_applicant", result=result)
    return result


@router.get("/applicants/{applicant_id}")
def get_applicant(applicant_id: str) -> dict[str, Any]:
    method_logger.enter("get_applicant", applicant_id=applicant_id)
    applicant_id = applicant_id.strip()
    applicant = applicant_service.get_submission(applicant_id)
    if applicant is None:
        logger.warning(f"Applicant not found: {applicant_id}")
        raise HTTPException(status_code=404, detail="Applicant record not found")
    method_logger.exit("get_applicant", result=applicant)
    return applicant


@router.put("/applicants/{applicant_id}")
def update_applicant(applicant_id: str, payload: ApplicantUpdate) -> dict[str, Any]:
    method_logger.enter("update_applicant", applicant_id=applicant_id)
    applicant_id = applicant_id.strip()
    result = applicant_service.update_submission(applicant_id, payload)
    method_logger.dynamic_string("Applicant updated: {applicant_id}", applicant_id=applicant_id)
    method_logger.exit("update_applicant", result=result)
    return result


@router.post("/applicant-cv")
def save_applicant_cv(payload: ApplicantCvSubmission) -> dict[str, Any]:
    method_logger.enter("save_applicant_cv", applicant_id=payload.applicant_id)
    result = applicant_cv_service.save_submission(payload)
    method_logger.dynamic_string("CV saved: {applicant_id} version {version}", applicant_id=payload.applicant_id, version=result.get("cv", {}).get("version", "N/A"))
    method_logger.exit("save_applicant_cv", result=result)
    return result


@router.get("/applicant-cv/{applicant_id}")
def get_applicant_cv(applicant_id: str, version: int | None = None) -> dict[str, Any]:
    method_logger.enter("get_applicant_cv", applicant_id=applicant_id, version=version)
    applicant_id = applicant_id.strip()
    if version is not None:
        cv = applicant_cv_service.get_submission_by_version(applicant_id, version)
    else:
        cv = applicant_cv_service.get_submission(applicant_id)
    if cv is None:
        logger.warning(f"CV not found: applicant_id={applicant_id}, version={version}")
        raise HTTPException(status_code=404, detail="Applicant CV not found")
    method_logger.exit("get_applicant_cv", result=cv)
    return cv


@router.get("/applicant-cv/{applicant_id}/versions")
def get_applicant_cv_versions(applicant_id: str) -> list[dict[str, Any]]:
    method_logger.enter("get_applicant_cv_versions", applicant_id=applicant_id)
    applicant_id = applicant_id.strip()
    result = applicant_cv_service.get_all_versions(applicant_id)
    method_logger.exit("get_applicant_cv_versions", result=len(result))
    return result


@router.post("/applicant-job-profiles")
def save_applicant_job_profile(payload: ApplicantJobProfileSubmission) -> dict[str, Any]:
    method_logger.enter("save_applicant_job_profile", applicant_id=payload.applicant_id, job_title=payload.job_title)
    result = applicant_job_profile_service.save_submission(payload)
    method_logger.dynamic_string("Job profile saved: {applicant_id} profile_id={profile_id}", applicant_id=payload.applicant_id, profile_id=result.get("profile", {}).get("profileId", "N/A"))
    method_logger.exit("save_applicant_job_profile", result=result)
    return result


@router.get("/applicant-job-profiles/{applicant_id}")
def get_applicant_job_profiles(applicant_id: str) -> list[dict[str, Any]]:
    method_logger.enter("get_applicant_job_profiles", applicant_id=applicant_id)
    applicant_id = applicant_id.strip()
    result = applicant_job_profile_service.get_submissions(applicant_id)
    method_logger.exit("get_applicant_job_profiles", result=len(result))
    return result


@router.put("/applicant-job-profiles/{profile_id}")
def update_applicant_job_profile(
    profile_id: str, payload: ApplicantJobProfileUpdate
) -> dict[str, Any]:
    method_logger.enter("update_applicant_job_profile", profile_id=profile_id)
    profile_id = profile_id.strip()
    result = applicant_job_profile_service.update_submission(profile_id, payload)
    method_logger.exit("update_applicant_job_profile", result=result)
    return result


@router.post("/sessions")
async def create_session(payload: CreateSessionRequest) -> dict[str, Any]:
    method_logger.enter("create_session", applicant_id=payload.applicant_id, cv_version=payload.cv_version)
    result = await session_service.create_session(payload.applicant_id, payload.cv_version, payload.job_profile_id)
    method_logger.dynamic_string("Session created: {session_id} for applicant {applicant_id}", session_id=result.get("session_id", "N/A"), applicant_id=payload.applicant_id)
    method_logger.exit("create_session", result=result)
    return result


@router.get("/applicant-sessions/{applicant_id}")
def get_applicant_sessions(applicant_id: str) -> list[dict[str, Any]]:
    method_logger.enter("get_applicant_sessions", applicant_id=applicant_id)
    applicant_id = applicant_id.strip()
    result = session_service.get_applicant_sessions(applicant_id)
    method_logger.exit("get_applicant_sessions", result=len(result))
    return result


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> dict[str, Any]:
    method_logger.enter("delete_session", session_id=session_id)
    session_id = session_id.strip()
    result = session_service.delete_session(session_id)
    if not result["success"]:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    method_logger.exit("delete_session", result=result)
    return result
