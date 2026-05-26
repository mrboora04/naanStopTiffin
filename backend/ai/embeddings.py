"""
ai/embeddings.py
================
EmbeddingEngine — swappable embedding provider.

Default (development / free): sentence-transformers all-MiniLM-L6-v2
  - 384 dimensions
  - Runs fully locally, no API key required
  - Good quality for semantic search tasks

To switch provider in future, set env var EMBEDDING_PROVIDER:
  EMBEDDING_PROVIDER=openai    → text-embedding-3-small  (needs OPENAI_API_KEY)
  EMBEDDING_PROVIDER=voyage    → voyage-3                (needs VOYAGE_API_KEY)
  EMBEDDING_PROVIDER=local     → sentence-transformers   (default, free)
"""

import os
import logging
from typing import Union

logger = logging.getLogger("naanstop.ai.embeddings")

PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower()


class EmbeddingEngine:
    """
    Single interface for text → vector embeddings.
    The model is loaded lazily on first call to avoid slowing startup.
    """

    def __init__(self):
        self._model = None
        self.provider = PROVIDER
        self.dimension: int = 384  # default for local model

    # ── Internal: load model once ─────────────────────────────────────────────

    def _load(self):
        if self._model is not None:
            return

        if self.provider == "local":
            logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)…")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self.dimension = 384
            logger.info("Embedding model loaded. Dimension=%d", self.dimension)

        elif self.provider == "openai":
            logger.info("Using OpenAI text-embedding-3-small…")
            from openai import OpenAI
            self._model = OpenAI()
            self.dimension = 1536

        elif self.provider == "voyage":
            logger.info("Using Voyage AI voyage-3…")
            import voyageai
            self._model = voyageai.Client()
            self.dimension = 1024

        else:
            raise ValueError(f"Unknown EMBEDDING_PROVIDER: {self.provider!r}")

    # ── Public API ────────────────────────────────────────────────────────────

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string → float vector."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of strings → list of float vectors."""
        self._load()
        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            return []

        if self.provider == "local":
            vecs = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return vecs.tolist()

        elif self.provider == "openai":
            resp = self._model.embeddings.create(
                model="text-embedding-3-small", input=texts
            )
            return [item.embedding for item in resp.data]

        elif self.provider == "voyage":
            result = self._model.embed(texts, model="voyage-3")
            return result.embeddings

        return []

    # ── Domain helpers ────────────────────────────────────────────────────────

    def member_text(self, member) -> str:
        """
        Create a rich text representation of a member for embedding.
        Captures dietary preference, plan, address area, and notes.
        """
        parts = [
            f"Member: {member.name}",
            f"Diet: {getattr(member, 'dietary_preference', 'unknown')}",
            f"Status: {getattr(member, 'member_status', 'unknown')}",
            f"Plan: {getattr(member, 'plan_id', '')}",
            f"Allergies: {getattr(member, 'allergies', '') or 'none'}",
            f"Notes: {getattr(member, 'delivery_notes', '') or 'none'}",
        ]
        return " | ".join(parts)

    def schedule_text(self, day) -> str:
        """
        Create a text representation of a ScheduleDay for embedding.
        Captures date, menus, and holiday status.
        """
        parts = [
            f"Date: {day.date}",
            f"Day: {getattr(day, 'day_of_week', '')}",
            f"Veg Lunch: {getattr(day, 'lunch_veg_dishes', '') or 'not set'}",
            f"Non-veg Lunch: {getattr(day, 'lunch_nonveg_dishes', '') or 'not set'}",
            f"Veg Dinner: {getattr(day, 'dinner_veg_dishes', '') or 'not set'}",
            f"Non-veg Dinner: {getattr(day, 'dinner_nonveg_dishes', '') or 'not set'}",
            f"Notes: {getattr(day, 'special_notes', '') or 'none'}",
            f"Holiday: {'yes' if getattr(day, 'is_holiday', False) else 'no'}",
        ]
        return " | ".join(parts)

    def feedback_text(self, fb) -> str:
        """Text representation of a feedback record."""
        parts = [
            f"Type: {getattr(fb, 'type', 'feedback')}",
            f"Rating: {getattr(fb, 'rating', 'N/A')}/10",
            f"Comment: {getattr(fb, 'comments', '') or 'none'}",
        ]
        return " | ".join(parts)


# Singleton instance — import and use anywhere
embedding_engine = EmbeddingEngine()
