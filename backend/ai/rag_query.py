"""
ai/rag_query.py
===============
Semantic query functions on top of the vector store.

These are the "brain" functions that power the AI endpoints.
No LLM is required yet — this is pure vector retrieval.
LLM generation (Phase 3) will slot in here by wrapping these
results in a prompt and calling an LLM API.

Functions:
  search_menu(query, k, date_filter)       → relevant schedule days
  find_similar_members(member_id, db, k)   → similar member profiles
  search_feedback(query, k, type_filter)   → relevant feedback items
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from ai.embeddings import embedding_engine
from ai.vector_store import vector_store, COLLECTION_SCHEDULE, COLLECTION_MEMBERS, COLLECTION_FEEDBACK

logger = logging.getLogger("naanstop.ai.rag_query")


# ── Menu / Schedule Search ────────────────────────────────────────────────────

def search_menu(
    query: str,
    k: int = 5,
    date_filter: Optional[str] = None,
) -> dict:
    """
    Semantic search across all ScheduleDay records.

    Example queries that work well:
      'veg paneer lunch friday'
      'non-veg dinner this week'
      'holiday menu'
      'What is being served for lunch?'

    Args:
        query:       Free-text search string
        k:           Number of results to return (max 10)
        date_filter: Optional ISO date string e.g. '2026-05-22' to restrict results

    Returns:
        {
            "query":   "...",
            "results": [{ "date": "...", "menu": "...", "score": 0.92 }, ...]
        }
    """
    k = min(k, 10)
    query_vec = embedding_engine.embed_text(query)

    where = {"date": {"$eq": date_filter}} if date_filter else None
    raw = vector_store.search(COLLECTION_SCHEDULE, query_vec, k=k, where=where)

    results = [
        {
            "date":     r["metadata"].get("date", ""),
            "day":      r["metadata"].get("day_of_week", ""),
            "menu":     r["document"],
            "score":    r["score"],
            "is_holiday": r["metadata"].get("is_holiday", "False") == "True",
        }
        for r in raw
    ]

    return {"query": query, "count": len(results), "results": results}


# ── Similar Member Search ─────────────────────────────────────────────────────

def find_similar_members(
    member_id: str,
    db: Session,
    k: int = 3,
) -> dict:
    """
    Find members with similar dietary profiles to the given member_id.

    Useful for:
      - Grouping members for batch communication
      - Cook planning: who else has the same requirements?
      - Suggesting plan upgrades ('3 similar members are on the vegan plan')

    Args:
        member_id: The member to find neighbours for
        db:        Database session
        k:         Number of similar members to return

    Returns:
        {
            "member_id": "...",
            "similar":   [{ "id": "...", "name": "...", "score": 0.91 }, ...]
        }
    """
    from models.member import Member

    source = db.query(Member).filter(Member.id == member_id).first()
    if not source:
        return {"member_id": member_id, "similar": [], "error": "Member not found"}

    source_text = embedding_engine.member_text(source)
    query_vec = embedding_engine.embed_text(source_text)

    # Search for k+1 because the member itself might appear in results
    raw = vector_store.search(COLLECTION_MEMBERS, query_vec, k=k + 1)

    similar = [
        {
            "id":                 r["id"],
            "name":               r["metadata"].get("name", ""),
            "member_status":      r["metadata"].get("member_status", ""),
            "dietary_preference": r["metadata"].get("dietary_preference", ""),
            "score":              r["score"],
        }
        for r in raw
        if r["id"] != member_id  # exclude the source member
    ][:k]

    return {
        "member_id":      member_id,
        "member_name":    source.name,
        "similar_count":  len(similar),
        "similar":        similar,
    }


# ── Feedback / Complaint Search ───────────────────────────────────────────────

def search_feedback(
    query: str,
    k: int = 5,
    type_filter: Optional[str] = None,
) -> dict:
    """
    Semantic search across all Feedback records.

    Find complaints/suggestions similar to a query without reading every row.
    Helps operations identify recurring patterns:
      'late delivery', 'spicy food complaint', 'packaging suggestion'

    Args:
        query:       Free-text search string
        k:           Number of results to return
        type_filter: Optional — 'feedback' | 'complaint' | 'suggestion'

    Returns:
        {
            "query":   "...",
            "results": [{ "type": "...", "rating": "...", "comment": "...", "score": 0.87 }, ...]
        }
    """
    k = min(k, 10)
    query_vec = embedding_engine.embed_text(query)

    where = {"type": {"$eq": type_filter}} if type_filter else None
    raw = vector_store.search(COLLECTION_FEEDBACK, query_vec, k=k, where=where)

    results = [
        {
            "id":     r["id"],
            "type":   r["metadata"].get("type", ""),
            "rating": r["metadata"].get("rating", "N/A"),
            "status": r["metadata"].get("status", ""),
            "text":   r["document"],
            "score":  r["score"],
        }
        for r in raw
    ]

    return {"query": query, "count": len(results), "results": results}


# ── Vector Store Status ───────────────────────────────────────────────────────

def get_store_stats() -> dict:
    """Return current document counts for each collection."""
    return {
        "schedule_days": vector_store.count(COLLECTION_SCHEDULE),
        "members":       vector_store.count(COLLECTION_MEMBERS),
        "feedback":      vector_store.count(COLLECTION_FEEDBACK),
        "embedding_provider": embedding_engine.provider,
        "embedding_dimension": embedding_engine.dimension,
    }
