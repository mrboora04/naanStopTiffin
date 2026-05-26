"""
migrate_add_logistic_columns.py
================================
One-time SQLite migration to add the two columns needed by the logistic regression classifiers:
  - day_of_week (TEXT)  — logistic regression feature
  - was_late   (INTEGER) — training label (NULL=unlabeled, 1=late, 0=on-time)

SQLite does not support adding columns via SQLAlchemy's create_all when the table already
exists, so this script uses ALTER TABLE directly.

Usage:
    python migrate_add_logistic_columns.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "naanstop.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(deliveries)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    print("Current deliveries columns:", existing_cols)

    if "day_of_week" not in existing_cols:
        cursor.execute("ALTER TABLE deliveries ADD COLUMN day_of_week TEXT DEFAULT ''")
        print("  + Added: day_of_week")
    else:
        print("  ~ Already exists: day_of_week")

    if "was_late" not in existing_cols:
        cursor.execute("ALTER TABLE deliveries ADD COLUMN was_late INTEGER DEFAULT NULL")
        print("  + Added: was_late  (NULL=unlabeled, 1=late, 0=on-time)")
    else:
        print("  ~ Already exists: was_late")

    conn.commit()
    conn.close()
    print("\nMigration complete.")

if __name__ == "__main__":
    migrate()
