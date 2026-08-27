import sqlite3

conn = sqlite3.connect(":memory:")

try:
    cursor = conn.cursor()
    cursor.execute("CREATE table users (id INT, name TEXT)")
finally:
    conn.close
    