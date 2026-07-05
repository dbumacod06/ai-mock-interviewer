import shutil
import time
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..logging_utils import get_method_logger

ALLOWED_DOCUMENT_SUFFIXES = {".doc", ".docx", ".pdf", ".txt"}
ALLOWED_DOCUMENT_CONTENT_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
    "text/plain",
}

method_logger = get_method_logger(__name__)


class DocumentService:
    async def upload_applicant_documents(
        self,
        applicant_id: str,
        resume_file: UploadFile,
        job_description_file: UploadFile,
    ) -> dict[str, object]:
        method_logger.enter("upload_applicant_documents", applicant_id=applicant_id)
        applicant_id = applicant_id.strip()
        if not applicant_id:
            raise HTTPException(status_code=400, detail="Applicant ID is required.")

        resume_path = self._save_document_file(resume_file, applicant_id, "resume", "resume")
        job_description_path = self._save_document_file(
            job_description_file,
            applicant_id,
            "job-description",
            "job description",
        )

        result = {
            "applicant_id": applicant_id,
            "resume_file": {
                "filename": resume_file.filename,
                "saved_path": resume_path,
            },
            "job_description_file": {
                "filename": job_description_file.filename,
                "saved_path": job_description_path,
            },
        }
        method_logger.exit("upload_applicant_documents", result=result)
        return result

    def _save_document_file(self, file: UploadFile, applicant_id: str, prefix: str, label: str) -> str:
        method_logger.enter("_save_document_file", applicant_id=applicant_id, prefix=prefix, filename=file.filename)
        if not file.filename:
            raise HTTPException(status_code=400, detail=f"{label.title()} filename is required.")

        suffix = Path(file.filename).suffix.lower()
        content_type = (file.content_type or "").lower()
        if suffix not in ALLOWED_DOCUMENT_SUFFIXES and content_type not in ALLOWED_DOCUMENT_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only Word documents, PDFs, and plain text files are supported.",
            )

        project_root = Path(__file__).resolve().parents[2]
        save_dir = project_root / "tmp" / "documents" / applicant_id
        save_dir.mkdir(parents=True, exist_ok=True)

        save_path = save_dir / f"{prefix}-{int(time.time() * 1000)}{suffix or '.txt'}"
        with open(save_path, "wb") as target:
            shutil.copyfileobj(file.file, target)

        method_logger.exit("_save_document_file", result=str(save_path))
        return str(save_path)


document_service = DocumentService()
