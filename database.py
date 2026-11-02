import json
import sqlite3
from datetime import datetime


class Database:
    """Saves calculations in a SQLite file."""

    def __init__(self, path):
        self.path = path
        connection = self.connect()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT NOT NULL,
                inputs TEXT NOT NULL,
                result TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        connection.close()

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, method, inputs, result):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        connection = self.connect()
        cursor = connection.execute(
            "INSERT INTO calculations (method, inputs, result, summary, created_at) VALUES (?, ?, ?, ?, ?)",
            (method, json.dumps(inputs), json.dumps(result), result["summary"], created_at),
        )
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()
        return new_id

    def get_all(self, method=None, limit=20):
        connection = self.connect()
        if method:
            rows = connection.execute(
                "SELECT * FROM calculations WHERE method = ? ORDER BY id DESC LIMIT ?", (method, limit)
            ).fetchall()
        else:
            rows = connection.execute("SELECT * FROM calculations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        connection.close()
        return [
            {"id": row["id"], "method": row["method"], "summary": row["summary"], "created_at": row["created_at"]}
            for row in rows
        ]

    def get_one(self, calculation_id):
        connection = self.connect()
        row = connection.execute("SELECT * FROM calculations WHERE id = ?", (calculation_id,)).fetchone()
        connection.close()
        if row is None:
            return None
        return {
            "id": row["id"],
            "method": row["method"],
            "inputs": json.loads(row["inputs"]),
            "result": json.loads(row["result"]),
            "summary": row["summary"],
            "created_at": row["created_at"],
        }

    def delete(self, calculation_id):
        connection = self.connect()
        cursor = connection.execute("DELETE FROM calculations WHERE id = ?", (calculation_id,))
        connection.commit()
        deleted = cursor.rowcount > 0
        connection.close()
        return deleted
