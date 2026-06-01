"""
migrate_add_decision_tree_columns.py
=====================================
One-time SQLite migration to add columns needed by the Decision Tree
Surplus Food Matcher classifier on the members table:

  - lat                 (REAL)     — GPS latitude  for distance_km calculation
  - lng                 (REAL)     — GPS longitude for distance_km calculation
  - last_offer_accepted (DATETIME) — Timestamp of last accepted flash sale
                                     NULL = never offered / model starts fresh
                                     Set  = prevents daily spamming, trains cadence

SQLite does not support ALTER TABLE ADD COLUMN via SQLAlchemy create_all when
the table already exists, so this script uses raw ALTER TABLE directly.

Usage:
    python migrate_add_decision_tree_columns.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "naanstop.db")


def migrate():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(members)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    print("Current members columns:", existing_cols)

    new_columns = [
        ("lat",                 "REAL    DEFAULT NULL"),
        ("lng",                 "REAL    DEFAULT NULL"),
        ("last_offer_accepted", "TEXT    DEFAULT NULL"),   # stored as ISO-8601 string
    ]

    for col_name, col_def in new_columns:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_def}")
            print(f"  + Added: {col_name}")
        else:
            print(f"  ~ Already exists: {col_name}")

    conn.commit()
    conn.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    migrate()
