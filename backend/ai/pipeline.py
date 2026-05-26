"""
ai/pipeline.py
==============
Indexing pipeline — reads from SQLite, embeds, stores in ChromaDB.

This runs automatically on startup (if the vector store is empty)
and can be re-triggered via POST /api/v1/ai/reindex.

Pipelines:
  run_schedule_pipeline(db)  → embeds all ScheduleDay rows
  run_member_pipeline(db)    → embeds all Member rows
  run_feedback_pipeline(db)  → embeds all Feedback rows
  run_all_pipelines(db)      → runs all three above
"""

import logging
from sqlalchemy.orm import Session

from ai.embeddings import embedding_engine
from ai.vector_store import vector_store, COLLECTION_SCHEDULE, COLLECTION_MEMBERS, COLLECTION_FEEDBACK

logger = logging.getLogger("naanstop.ai.pipeline")


# ── Schedule (Menu) Pipeline ──────────────────────────────────────────────────

def run_schedule_pipeline(db: Session) -> int:
    """
    Embeds all ScheduleDay rows so the AI can answer:
    'What veg dishes are available on Fridays?'
    'Show me all days with paneer.'

    Returns the number of documents indexed.
    """
    from models.schedule import ScheduleDay

    days = db.query(ScheduleDay).all()
    if not days:
        logger.info("No schedule days found — skipping schedule pipeline.")
        return 0

    texts = [embedding_engine.schedule_text(d) for d in days]
    vectors = embedding_engine.embed_batch(texts)

    metadatas = [
        {
            "date":       d.date,
            "day_of_week": getattr(d, "day_of_week", ""),
            "is_holiday": str(getattr(d, "is_holiday", False)),
        }
        for d in days
    ]

    vector_store.upsert(
        collection=COLLECTION_SCHEDULE,
        ids=[d.id for d in days],
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )

    logger.info("Schedule pipeline complete: %d days indexed.", len(days))
    return len(days)


# ── Member Pipeline ───────────────────────────────────────────────────────────

def run_member_pipeline(db: Session) -> int:
    """
    Embeds all Member rows so the AI can:
    - Find members with similar dietary profiles
    - Cluster members for targeted communication

    Returns the number of documents indexed.
    """
    from models.member import Member

    members = db.query(Member).all()
    if not members:
        logger.info("No members found — skipping member pipeline.")
        return 0

    texts = [embedding_engine.member_text(m) for m in members]
    vectors = embedding_engine.embed_batch(texts)

    metadatas = [
        {
            "name":               m.name,
            "member_status":      getattr(m, "member_status", "unknown"),
            "dietary_preference": getattr(m, "dietary_preference", "unknown"),
        }
        for m in members
    ]

    vector_store.upsert(
        collection=COLLECTION_MEMBERS,
        ids=[m.id for m in members],
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )

    logger.info("Member pipeline complete: %d members indexed.", len(members))
    return len(members)


# ── Feedback Pipeline ─────────────────────────────────────────────────────────

def run_feedback_pipeline(db: Session) -> int:
    """
    Embeds all Feedback rows for semantic complaint/suggestion search.
    Helps identify recurring issues without reading every row manually.

    Returns the number of documents indexed.
    """
    from models.feedback import Feedback

    items = db.query(Feedback).all()
    if not items:
        logger.info("No feedback found — skipping feedback pipeline.")
        return 0

    texts = [embedding_engine.feedback_text(f) for f in items]
    vectors = embedding_engine.embed_batch(texts)

    metadatas = [
        {
            "type":   getattr(f, "type", "feedback"),
            "rating": str(getattr(f, "rating", "N/A")),
            "status": getattr(f, "status", "new"),
        }
        for f in items
    ]

    vector_store.upsert(
        collection=COLLECTION_FEEDBACK,
        ids=[f.id for f in items],
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )

    logger.info("Feedback pipeline complete: %d items indexed.", len(items))
    return len(items)


# ── Master runner ─────────────────────────────────────────────────────────────

def run_all_pipelines(db: Session) -> dict:
    """
    Run all three pipelines and return a summary.
    Called on startup and via POST /api/v1/ai/reindex.
    """
    logger.info("Starting full AI indexing pipeline…")
    summary = {
        "schedule_days": run_schedule_pipeline(db),
        "members":       run_member_pipeline(db),
        "feedback":      run_feedback_pipeline(db),
    }
    logger.info("AI indexing complete: %s", summary)
    return summary


def needs_indexing() -> bool:
    """
    Returns True if any collection is empty.
    Used to decide whether to auto-run on startup.
    """
    return (
        vector_store.count(COLLECTION_SCHEDULE) == 0
        or vector_store.count(COLLECTION_MEMBERS) == 0
    )
