import sqlite3
import os

db_path = "backend/naanstop.db"
print("DB Exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("\nTables in DB:")
for table in tables:
    cursor.execute(f"SELECT count(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f" - {table}: {count} records")

# Inspect columns for key tables
for table in ["deliveries", "members", "comments"]:
    if table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [c[1] for c in cursor.fetchall()]
        print(f"\nColumns in {table}: {columns}")
        
        # Sample data
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        rows = cursor.fetchall()
        print(f"Sample in {table}: {rows}")

conn.close()
