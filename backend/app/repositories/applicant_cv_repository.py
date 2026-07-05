from typing import Any

from ..database import DatabaseSessionManager, database_session_manager


class ApplicantCvRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_by_applicant_id(self, applicant_id: str) -> Any:
        if not applicant_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CV_TABLE")
        return (
            client.table(table_name)
            .select("*")
            .eq("applicant_id", applicant_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )

    def get_all_by_applicant_id(self, applicant_id: str) -> Any:
        if not applicant_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CV_TABLE")
        return (
            client.table(table_name)
            .select("*")
            .eq("applicant_id", applicant_id)
            .order("version", desc=True)
            .execute()
        )

    def get_by_applicant_and_version(self, applicant_id: str, version: int) -> Any:
        if not applicant_id or not isinstance(version, int):
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CV_TABLE")
        return (
            client.table(table_name)
            .select("*")
            .eq("applicant_id", applicant_id)
            .eq("version", version)
            .maybe_single()
            .execute()
        )

    def get_latest_version(self, applicant_id: str) -> int:
        if not applicant_id:
            return 0
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CV_TABLE")
        response = (
            client.table(table_name)
            .select("version")
            .eq("applicant_id", applicant_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        if getattr(response, "data", None) and response.data:
            return response.data[0].get("version", 0)
        return 0

    def insert(self, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CV_TABLE")
        return client.table(table_name).insert(data).execute()


applicant_cv_repository = ApplicantCvRepository()
