import os
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class DatabaseSessionManager:
    _instance: Optional["DatabaseSessionManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "DatabaseSessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self) -> Client:
        if self._client is None:
            self._client = self._create_client()

        return self._client

    def get_table_name(self, environment_key: str) -> str:
        table_name = os.getenv(environment_key)
        if not table_name:
            raise ValueError(f"Missing table name environment variable: {environment_key}")
        return table_name

    def _create_client(self) -> Client:
        url = os.getenv("SB_PROJECT_URL")
        key = os.getenv("SB_ANON_KEY")

        if not url or not key:
            raise ValueError(
                "Missing Supabase credentials. Ensure SB_PROJECT_URL and SB_ANON_KEY are set."
            )

        return create_client(url, key)


database_session_manager = DatabaseSessionManager()
