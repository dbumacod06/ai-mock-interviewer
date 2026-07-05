from typing import Any

from ..database import DatabaseSessionManager, database_session_manager


class ApplicantRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_by_id(self, applicant_id: str, columns: str = "*") -> Any:
        if not applicant_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_TABLE")
        return client.table(table_name).select(columns).eq("id", applicant_id).maybe_single().execute()

    def insert(self, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_TABLE")
        return client.table(table_name).insert(data).execute()

    def update(self, applicant_id: str, data: dict[str, Any]) -> Any:
        if not applicant_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_TABLE")
        return client.table(table_name).update(data).eq("id", applicant_id).execute()


applicant_repository = ApplicantRepository()
