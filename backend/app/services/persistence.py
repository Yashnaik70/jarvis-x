import os
import sqlite3
from typing import Optional, List, Tuple

DB_FILE = os.path.join(os.path.dirname(__file__), "../../jarvis_x.db")

class PersistenceLayer:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = os.path.abspath(db_file)
        self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
        self._initialize()

    def _initialize(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

    def store_memory(self, key: str, value: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO memory (memory_key, memory_value) VALUES (?, ?)",
            (key, value),
        )
        self.connection.commit()

    def retrieve_memory(self, key: str) -> Optional[str]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT memory_value FROM memory WHERE memory_key = ? ORDER BY created_at DESC LIMIT 1",
            (key,),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def list_memory(self) -> List[Tuple[str, str, str]]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT memory_key, memory_value, created_at FROM memory ORDER BY created_at DESC"
        )
        return cursor.fetchall()
