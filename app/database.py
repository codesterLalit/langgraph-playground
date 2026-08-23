import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'tool', 'system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inbox_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outbox_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'sent', 'rejected')),
    created_at TEXT NOT NULL,
    reviewed_at TEXT
);
"""


def now() -> str:
    return datetime.now(UTC).isoformat()


class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(SCHEMA)

    def create_thread(self, thread_id: str, title: str = "") -> None:
        timestamp = now()
        with self.connection() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO threads(id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (thread_id, title, timestamp, timestamp),
            )

    def add_message(self, thread_id: str, role: str, content: str) -> None:
        self.create_thread(thread_id)
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO messages(thread_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (thread_id, role, content, now()),
            )
            connection.execute(
                "UPDATE threads SET updated_at = ? WHERE id = ?",
                (now(), thread_id),
            )

    def list_messages(self, thread_id: str) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute(
                "SELECT role, content, created_at FROM messages WHERE thread_id = ? ORDER BY id",
                (thread_id,),
            ).fetchall()

    def seed_inbox(self) -> None:
        with self.connection() as connection:
            count = connection.execute("SELECT COUNT(*) FROM inbox_messages").fetchone()[0]
            if count == 0:
                connection.execute(
                    "INSERT INTO inbox_messages(sender, subject, body, created_at) VALUES (?, ?, ?, ?)",
                    (
                        "jane@example.com",
                        "Coffee next week?",
                        "Hi Julie, I am going to be in town next week and was wondering if we could grab a coffee?",
                        now(),
                    ),
                )

    def list_inbox(self) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute(
                "SELECT id, sender, subject, body, is_read, created_at FROM inbox_messages ORDER BY id DESC"
            ).fetchall()

    def add_outbox(self, recipient: str, subject: str, body: str) -> int:
        with self.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO outbox_messages(recipient, subject, body, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
                (recipient, subject, body, now()),
            )
            return int(cursor.lastrowid)

    def review_outbox(self, message_id: int, approved: bool) -> None:
        status = "sent" if approved else "rejected"
        with self.connection() as connection:
            connection.execute(
                "UPDATE outbox_messages SET status = ?, reviewed_at = ? WHERE id = ? AND status = 'pending'",
                (status, now(), message_id),
            )

    def list_outbox(self) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute(
                "SELECT id, recipient, subject, body, status, created_at, reviewed_at "
                "FROM outbox_messages ORDER BY id DESC"
            ).fetchall()
