from typing import Any

from ..database import DatabaseSessionManager, database_session_manager


class SessionRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_by_applicant_id(self, applicant_id: str) -> Any:
        if not applicant_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_SESSIONS_TABLE")
        return (
            client.table(table_name)
            .select("*")
            .eq("applicant_id", applicant_id)
            .order("created_at", desc=True)
            .execute()
        )

    def get_by_session_id(self, session_id: str) -> Any:
        if not session_id:
            return None
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_SESSIONS_TABLE")
        return client.table(table_name).select("*").eq("session_id", session_id).execute()

    def insert(self, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_SESSIONS_TABLE")
        return client.table(table_name).insert(data).execute()

    def update(self, session_id: str, data: dict[str, Any]) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_SESSIONS_TABLE")
        return client.table(table_name).update(data).eq("session_id", session_id).execute()

    def delete(self, session_id: str) -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_SESSIONS_TABLE")
        return client.table(table_name).delete().eq("session_id", session_id).execute()


session_repository = SessionRepository()
