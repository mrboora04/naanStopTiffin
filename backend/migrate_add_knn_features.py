"""
migrate_add_knn_features.py
Phase 4: KNN Lone Bird Predictor
──────────────────────────────────────────────────────────────────────────────
Adds the following columns to support the KNN "Lone Bird" features:

  members  table:
    + last_nudge_sent     DATETIME  — Timestamp of last "Your usual is ready" nudge
    + last_wildcard_sent  DATETIME  — Timestamp of last weekly "wildcard" dish nudge

  deliveries table:
    + ordered_at          DATETIME  — Exact minute the ad-hoc order was placed
    + is_ad_hoc           INTEGER   — 1 = walk-in / lone-bird order, 0 = subscription delivery

Run once:
  python backend/migrate_add_knn_features.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "naanstop.db")


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def run():
    print(f"Connecting to: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    migrations = [
        ("members",   "last_nudge_sent",    "ALTER TABLE members   ADD COLUMN last_nudge_sent    DATETIME"),
        ("members",   "last_wildcard_sent", "ALTER TABLE members   ADD COLUMN last_wildcard_sent DATETIME"),
        ("deliveries","ordered_at",         "ALTER TABLE deliveries ADD COLUMN ordered_at         DATETIME"),
        ("deliveries","is_ad_hoc",          "ALTER TABLE deliveries ADD COLUMN is_ad_hoc          INTEGER DEFAULT 0"),
    ]

    for table, col, sql in migrations:
        if column_exists(cur, table, col):
            print(f"  [SKIP]  {table}.{col} already exists")
        else:
            cur.execute(sql)
            print(f"  [ADD]   {table}.{col}")

    conn.commit()
    conn.close()
    print("\nMigration complete [OK]")


if __name__ == "__main__":
    run()
