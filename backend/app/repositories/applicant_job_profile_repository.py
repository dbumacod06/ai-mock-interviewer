from typing import Any

from ..database import DatabaseSessionManager, database_session_manager


class ApplicantJobProfileRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_by_applicant_id(self, applicant_id: str) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_JOB_PROFILE_TABLE")
        return client.table(table_name).select("*").eq("applicant_id", applicant_id).execute()

    def get_by_id(self, profile_id: str) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_JOB_PROFILE_TABLE")
        return client.table(table_name).select("*").eq("id", profile_id).maybe_single().execute()

    def insert(self, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_JOB_PROFILE_TABLE")
        return client.table(table_name).insert(data).execute()

    def update(self, profile_id: str, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_JOB_PROFILE_TABLE")
        return client.table(table_name).update(data).eq("id", profile_id).execute()


applicant_job_profile_repository = ApplicantJobProfileRepository()
