from datetime import datetime, timezone
from typing import Any, Dict

from ..database import DatabaseSessionManager, database_session_manager


class ApplicantGraphStateRepository:
    def __init__(self, session_manager: DatabaseSessionManager = database_session_manager) -> None:
        self.session_manager = session_manager

    def get_graph_state(self, session_id: str) -> dict[str, Any]:
        """Fetches the internal LangGraph state document snapshot."""
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_GRAPH_STATES_TABLE")
        response = (
            client.table(table_name)
            .select("graph_state")
            .eq("session_id", session_id)
            .maybe_single()
            .execute()
        )
        if response.data and response.data.get("graph_state"):
            return response.data["graph_state"]
        return {}

    def save_graph_state(self, session_id: str, graph_state: dict[str, Any]) -> Any:
        """Upserts the consolidated LangGraph state checkpoint back to its dedicated row."""
        client = self.session_manager.get_client()
        table_name = self.session_manager.get_table_name("APPLICANT_GRAPH_STATES_TABLE")

        filtered_state = {**graph_state}
        # 2. Force the messages key to be an empty list
        filtered_state["messages"] = []

        return client.table(table_name).upsert({
            "session_id": session_id,
            "graph_state": filtered_state,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict='session_id').execute()


applicant_graph_state_repository = ApplicantGraphStateRepository()
