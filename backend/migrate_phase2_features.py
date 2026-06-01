"""
migrate_phase2_features.py
===========================
One-time SQLite migration to add columns for two Phase 2 features:

  Feature 1 — Zero-Cost Delivery Telemetry (models/delivery.py):
    - dispatched_at        (TEXT / ISO datetime)  — when driver departs the kitchen
    - delivered_at         (TEXT / ISO datetime)  — when driver marks run as done
    - estimated_drive_time (INTEGER)              — static OSRM estimate in minutes

  Feature 2 — Food Story RAG Pipeline (models/schedule.py):
    - core_ingredients (TEXT) — comma-separated key ingredients for that day's batch
    - expert_benefits  (TEXT) — AI-generated or manually written health benefit summary

SQLite stores datetimes as TEXT in ISO 8601 format. SQLAlchemy handles the
conversion transparently via the DateTime column type.

Usage:
    python migrate_phase2_features.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "naanstop.db")


def _add_column_if_missing(cursor, table: str, column: str, col_type: str):
    cursor.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in cursor.fetchall()]
    if column not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"  + [{table}] Added: {column}")
    else:
        print(f"  ~ [{table}] Already exists: {column}")


def migrate():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 55)
    print("NaanStop Tiffin — Phase 2 Feature Migration")
    print("=" * 55)

    # ── Feature 1: Zero-Cost Delivery Telemetry ───────────────
    print("\n[1] Zero-Cost Delivery Telemetry (deliveries table):")
    _add_column_if_missing(cursor, "deliveries", "dispatched_at",        "TEXT DEFAULT NULL")
    _add_column_if_missing(cursor, "deliveries", "delivered_at",         "TEXT DEFAULT NULL")
    _add_column_if_missing(cursor, "deliveries", "estimated_drive_time", "INTEGER DEFAULT NULL")

    # ── Feature 2: Food Story RAG Pipeline ────────────────────
    print("\n[2] Food Story RAG Pipeline (schedule_days table):")
    _add_column_if_missing(cursor, "schedule_days", "core_ingredients", "TEXT DEFAULT ''")
    _add_column_if_missing(cursor, "schedule_days", "expert_benefits",  "TEXT DEFAULT ''")

    conn.commit()
    conn.close()
    print("\nMigration complete. ✓")


if __name__ == "__main__":
    migrate()
