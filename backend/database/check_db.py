import sqlite3
import os

db_path = "sales.db"

print("Database exists:", os.path.exists(db_path))

if not os.path.exists(db_path):
    print(" sales.db not found")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nTables:")
for table in tables:
    print("-", table[0])

print("\nRow Counts:")

for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count}")
    except Exception as e:
        print(table_name, e)

conn.close()