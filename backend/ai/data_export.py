"""
data_export.py
==============
Exports all database tables as pandas DataFrames.
This is the entry point for training ML models in Phase 3.

Usage:
    python -m ai.data_export

Output: CSV files in backend/ai/exports/
"""

import os
import sys

# Add backend root to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from models.member import Member
from models.delivery import Delivery
from models.feedback import Feedback
from models.schedule import ScheduleDay


def export_all():
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed. Run: pip install pandas")
        return

    db = SessionLocal()
    export_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(export_dir, exist_ok=True)

    tables = {
        "members":   Member,
        "deliveries": Delivery,
        "feedback":  Feedback,
        "schedule":  ScheduleDay,
    }

    for name, model in tables.items():
        rows = db.query(model).all()
        data = [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]
        df = pd.DataFrame(data)
        path = os.path.join(export_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  ✓ Exported {len(df)} rows → {path}")

    db.close()
    print("\nExport complete. Ready for model training.")


if __name__ == "__main__":
    export_all()
