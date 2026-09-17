# Kotha 2.0
# Draft memory system
# In-house SQLite memory — no external database library required.

import sqlite3


class Memory:
    def __init__(self, database="kotha_memory.db"):
        self.database = database
        self.connection = sqlite3.connect(database)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL
            )
        """)

        self.connection.commit()

    def remember(self, key, value):
        self.connection.execute(
            "INSERT INTO memories (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.connection.commit()

    def recall(self, key):
        cursor = self.connection.execute(
            """
            SELECT value
            FROM memories
            WHERE key = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (key,)
        )

        result = cursor.fetchone()
        return result[0] if result else None

    def forget(self, key):
        self.connection.execute(
            "DELETE FROM memories WHERE key = ?",
            (key,)
        )
        self.connection.commit()

    def all_memories(self):
        cursor = self.connection.execute(
            "SELECT key, value FROM memories ORDER BY id"
        )

        return cursor.fetchall()

    def close(self):
        self.connection.close()