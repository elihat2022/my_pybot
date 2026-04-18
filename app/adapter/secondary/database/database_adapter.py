import sqlite3
import json

from typing import List, Dict, Any
from app.ports.outbound.memory_port import MemoryPort

class SQLiteMemoryAdapter(MemoryPort):
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._initialize_db()
    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message_payload TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    session_id TEXT PRIMARY KEY,
                    summary_text TEXT NOT NULL,
                    last_summarized_id INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def save_message(self, session_id: str, message_payload: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO messages (session_id, message_payload) VALUES (?, ?)
            """, (session_id, json.dumps(message_payload)))
            conn.commit()
    
    def get_message_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT message_payload FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            rows = cur.fetchall()
        history = []
        for row in rows:
            message_dict = json.loads(row[0])
            history.append(message_dict)
        history.reverse()  # Return in chronological order
        return history

    def get_last_session_id(self) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT session_id FROM messages ORDER BY timestamp DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                return row[0]
        return None