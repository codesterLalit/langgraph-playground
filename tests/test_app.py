import tempfile
import unittest
from pathlib import Path

from app.database import Database
from app.sql_tools import is_read_only


class DatabaseTests(unittest.TestCase):
    def test_schema_seed_and_thread_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "app.db")
            database.initialize()
            database.seed_inbox()
            database.add_message("thread-1", "user", "hello")
            database.add_message("thread-1", "assistant", "hi")

            self.assertEqual(len(database.list_inbox()), 1)
            self.assertEqual(
                [row["content"] for row in database.list_messages("thread-1")],
                ["hello", "hi"],
            )
            self.assertEqual(database.list_messages("thread-2"), [])

    def test_outbox_review_transitions(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "app.db")
            database.initialize()
            message_id = database.add_outbox("jane@example.com", "Re: coffee", "Sure!")
            database.review_outbox(message_id, approved=True)

            with database.connection() as connection:
                row = connection.execute(
                    "SELECT status FROM outbox_messages WHERE id = ?", (message_id,)
                ).fetchone()
            self.assertEqual(row["status"], "sent")


class SqlSafetyTests(unittest.TestCase):
    def test_only_read_queries_are_allowed(self):
        self.assertTrue(is_read_only("SELECT * FROM inbox_messages"))
        self.assertTrue(is_read_only("WITH rows AS (SELECT 1) SELECT * FROM rows"))
        self.assertFalse(is_read_only("UPDATE inbox_messages SET is_read = 1"))
        self.assertFalse(is_read_only("DROP TABLE inbox_messages"))


if __name__ == "__main__":
    unittest.main()
