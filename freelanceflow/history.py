import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, client TEXT, brief TEXT, workflow TEXT, output TEXT, created_at TEXT)")

    def save(self, client: str, brief: str, workflow: str, output: dict) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "INSERT INTO projects (client, brief, workflow, output, created_at) VALUES (?, ?, ?, ?, ?)",
                (client, brief, workflow, json.dumps(output), datetime.now(timezone.utc).isoformat()),
            )

    def list_records(self) -> list[dict]:
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT id, client, workflow, output, created_at FROM projects ORDER BY id DESC"
            ).fetchall()
        return [
            {
                "id": row["id"],
                "client": row["client"],
                "workflow": row["workflow"],
                "output": json.loads(row["output"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def delete(self, record_id: int) -> bool:
        with sqlite3.connect(self.path) as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (record_id,))
            return cursor.rowcount > 0

    def clear(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute("DELETE FROM projects")
