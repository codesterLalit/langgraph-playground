import sqlite3
from pathlib import Path
from typing import Any

from langchain.tools import tool

WRITE_STATEMENTS = {
    "alter",
    "create",
    "delete",
    "drop",
    "insert",
    "replace",
    "truncate",
    "update",
}


def is_read_only(query: str) -> bool:
    statement = query.strip().lower()
    if not statement:
        return False
    first_word = statement.split(None, 1)[0]
    return first_word not in WRITE_STATEMENTS and statement.startswith(("select", "with", "pragma"))


def make_sql_tool(database_path: Path | str):
    @tool
    def query_database(query: str) -> list[dict[str, Any]] | str:
        """Run a read-only SQL query against the local SQLite database."""
        if not is_read_only(query):
            return "Rejected: only read-only SELECT, WITH, or PRAGMA queries are allowed."
        try:
            with sqlite3.connect(database_path) as connection:
                connection.row_factory = sqlite3.Row
                return [dict(row) for row in connection.execute(query).fetchall()]
        except sqlite3.Error as exc:
            return f"Database error: {exc}"

    return query_database
