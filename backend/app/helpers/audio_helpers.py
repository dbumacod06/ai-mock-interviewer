import os
import shutil
import tempfile
import time

from fastapi import HTTPException, UploadFile
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def save_uploaded_audio_file(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A recording file is required.")

    content_type = (file.content_type or "").lower()
    is_audio = content_type.startswith("audio/") or file.filename.lower().endswith(
        (".wav", ".webm", ".ogg", ".m4a", ".mp3", ".mp4", ".aac")
    )
    if not is_audio:
        raise HTTPException(status_code=400, detail="Only recorded audio files are supported for transcription.")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    save_dir = os.path.join(project_root, "tmp")
    os.makedirs(save_dir, exist_ok=True)

    original_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename or "audio.tmp")[1] or ".tmp",
        ) as tmp:
            original_path = tmp.name
            shutil.copyfileobj(file.file, tmp)

        base_name = f"recording-{int(time.time() * 1000)}"
        ext = os.path.splitext(file.filename or "")[1] or ".mp3"
        saved_audio_path = os.path.join(save_dir, f"{base_name}{ext}")
        shutil.copyfile(original_path, saved_audio_path)
        return saved_audio_path
    finally:
        if original_path and os.path.exists(original_path):
            os.remove(original_path)


def transcribe_audio_file(file_path: str, applicant_details, job_profiles) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Configure your OpenAI API key before using transcription.")

    client = OpenAI()
    print(applicant_details)
    transcription_prompt = f"""
        The candidate's first name is {applicant_details.get("first_name")}.
        The candidate's last name is {applicant_details.get("last_name")}.
        The candidate's preferred name is {applicant_details.get("preferred_name")}.
        The candidate is applying for the {job_profiles[0].get("job_title")} position at {job_profiles[0].get("company")}.
        The candidate is currently a/an {applicant_details.get("current_role")} at {applicant_details.get("current_company")}.
        The candidate has previously worked at {applicant_details.get("previous_companies")}
    """

    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            prompt=transcription_prompt,
        )

    return getattr(response, "text", "").strip()
