from typing import Any

from ..database import DatabaseSessionManager, database_session_manager


class ConversationRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_by_id(self, conversation_id: str, columns: str = "*") -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CONVERSATIONS_TABLE")
        return client.table(table_name).select(columns).eq("id", conversation_id).execute()

    def insert(self, data: dict[str, Any]) -> Any:
        import logging
        logger = logging.getLogger(__name__)
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CONVERSATIONS_TABLE")
        logger.info(f"Inserting into {table_name}: {data}")
        result = client.table(table_name).insert(data).execute()
        logger.info(f"Insert result: {getattr(result, 'data', 'no data')} | status={getattr(result, 'status', 'unknown')}")
        return result

    def get_by_session(self, session_id: str, limit: int = 25, columns: str = "*") -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CONVERSATIONS_TABLE")
        query = (
            client.table(table_name) 
                .select(columns) 
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                # .limit(limit)
        )
        return query.execute()

    def get_by_applicant(self, applicant_id: str, columns: str = "*") -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CONVERSATIONS_TABLE")
        return client.table(table_name).select(columns).eq("applicant_id", applicant_id).order("created_at").execute()

    def get_by_applicant_and_session(self, applicant_id: str, session_id: str, columns: str = "*") -> Any:
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_CONVERSATIONS_TABLE")
        return (
            client.table(table_name)
            .select(columns)
            .eq("applicant_id", applicant_id)
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )


conversation_repository = ConversationRepository()
