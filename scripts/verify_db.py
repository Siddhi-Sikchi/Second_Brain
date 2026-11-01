import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "backend" / "second_brain.db"
print(f"Connecting to database: {db_path}")
con = sqlite3.connect(db_path)
cur = con.cursor()
tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in database:", tables)
con.close()
