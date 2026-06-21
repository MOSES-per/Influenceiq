import json
import os
from datetime import datetime
import sqlite3

class RawJSONStore:
    def __init__(self, base_path="data/raw_json"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, platform, username, data):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{username}_{timestamp}.json"
        filepath = os.path.join(self.base_path, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

class RawSQLiteStore:
    def __init__(self, db_path="storage/database.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            conn.commit()

    def save(self, platform, username, data):
        collected_at = datetime.utcnow().isoformat()
        payload = json.dumps(data)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raw_data (platform, username, collected_at, payload)
                VALUES (?, ?, ?, ?)
            """, (platform, username, collected_at, payload))
            conn.commit()

    def fetch_latest(self, platform, username):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payload FROM raw_data
                WHERE platform = ? AND username = ?
                ORDER BY collected_at DESC
                LIMIT 1
            """, (platform, username))

            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
