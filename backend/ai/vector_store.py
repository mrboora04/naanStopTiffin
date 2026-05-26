"""
ai/vector_store.py
==================
ChromaDB vector store wrapper.

Why ChromaDB?
  - Runs in-process, no Docker or separate server needed
  - Persists to disk at ai/chroma_db/
  - Zero-config for development
  - Swap to Qdrant/Pinecone in production by changing this file only

Collections used:
  - "schedule"  → ScheduleDay records (menu search)
  - "members"   → Member profiles (similarity search)
  - "feedback"  → Feedback comments (sentiment/pattern analysis)
"""

import os
import logging
from typing import Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger("naanstop.ai.vector_store")

# Persist path: backend/ai/chroma_db/
_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

# Collection names — used as namespaces in ChromaDB
COLLECTION_SCHEDULE  = "schedule"
COLLECTION_MEMBERS   = "members"
COLLECTION_FEEDBACK  = "feedback"


class VectorStore:
    """
    Thin wrapper around ChromaDB.
    Handles collection management, upsert, and semantic search.
    """

    def __init__(self):
        os.makedirs(_DB_PATH, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB initialised at %s", _DB_PATH)

    def _col(self, name: str):
        """Get or create a collection by name."""
        return self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},  # cosine similarity
        )

    # ── Write ─────────────────────────────────────────────────────────────────

    def upsert(
        self,
        collection: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """
        Insert or update documents in a collection.
        'ids' must be unique string identifiers for each document.
        """
        col = self._col(collection)
        col.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas or [{} for _ in ids],
        )
        logger.info("Upserted %d docs into collection '%s'", len(ids), collection)

    def clear(self, collection: str) -> None:
        """Delete all documents from a collection (used before re-indexing)."""
        try:
            self._client.delete_collection(collection)
            logger.info("Cleared collection '%s'", collection)
        except Exception:
            pass  # Collection didn't exist yet

    # ── Read ──────────────────────────────────────────────────────────────────

    def search(
        self,
        collection: str,
        query_embedding: list[float],
        k: int = 5,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """
        Semantic search.

        Returns a list of dicts:
          [
            {
              "id":       "...",
              "document": "...",
              "metadata": {...},
              "distance": 0.12,   # lower = more similar (cosine)
              "score":    0.88,   # 1 - distance, easier to read
            },
            ...
          ]
        """
        col = self._col(collection)

        kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(k, max(col.count(), 1)),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = col.query(**kwargs)

        output = []
        if results["ids"] and results["ids"][0]:
            for idx in range(len(results["ids"][0])):
                dist = results["distances"][0][idx]
                output.append({
                    "id":       results["ids"][0][idx],
                    "document": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx],
                    "distance": round(dist, 4),
                    "score":    round(1 - dist, 4),
                })
        return output

    def count(self, collection: str) -> int:
        """Return number of documents in a collection."""
        try:
            return self._col(collection).count()
        except Exception:
            return 0


# Singleton — import from anywhere
vector_store = VectorStore()
