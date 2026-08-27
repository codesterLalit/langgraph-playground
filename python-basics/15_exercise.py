import sqlite3
from types import TracebackType
from typing import Any, Literal

class ManagedSqlite:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn:sqlite3.Connection | None = None
        
    def __enter__(self) -> sqlite3.Connection:
        print(f"[Setup] Opening connection to {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(
        self, 
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
            ) -> Literal[False]:
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                
            print(f"[TEARDOWN] Closing connection to {self.db_name}")
            self.conn.close()
        return False

try:
    with ManagedSqlite(":memory:") as db:
        db.execute("CREATE TABLE logs (id INT, message TEXT)")
        db.execute("INSERT INTO logs (id, message) VALUES (?, ?)", (1, "Saving"))
        
        cursor = db.execute("SELECT * FROM logs WHERE id =?", (1, ))
        row = cursor.fetchone()
        print(f"logs record : {row}")
        
        print("[EXECUTE] Table created successfully")
except ValueError as error:
    print(f"Caught error: {error}")