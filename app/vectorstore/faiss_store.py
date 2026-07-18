"""
Optional FAISS-backed vector store for retrieving relevant financial tips,
past report summaries, or educational content. Not required for the core
pipeline to function — agents work fine without this module.
"""

from __future__ import annotations
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FinanceKnowledgeStore:
    """
    A minimal wrapper around a FAISS index for storing/retrieving short
    finance tips or past report summaries as embeddings.

    Falls back to a naive keyword-match store if `faiss` isn't installed,
    so the rest of the app never hard-depends on it.
    """

    def __init__(self):
        self._texts: list[str] = []
        self._index = None
        self._faiss_available = False

        try:
            import faiss  # noqa: F401
            self._faiss_available = True
        except ImportError:
            logger.warning("faiss-cpu not installed — using naive keyword fallback store.")

    def add_texts(self, texts: list[str]) -> None:
        self._texts.extend(texts)
        # A full implementation would embed `texts` and add vectors to
        # a faiss.IndexFlatL2 (or similar) here when self._faiss_available.

    def search(self, query: str, k: int = 3) -> list[str]:
        """
        Return up to `k` stored texts most relevant to `query`.
        Naive substring/keyword match fallback; swap in real embedding
        similarity search once an embeddings provider is configured.
        """
        query_terms = set(query.lower().split())
        scored = []
        for text in self._texts:
            text_terms = set(text.lower().split())
            overlap = len(query_terms & text_terms)
            if overlap:
                scored.append((overlap, text))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[:k]]


# Preloaded with a handful of generic finance tips as a starting knowledge base
knowledge_store = FinanceKnowledgeStore()
knowledge_store.add_texts([
    "Aim to keep an emergency fund covering 3 to 6 months of expenses.",
    "The 50/30/20 rule allocates 50% to needs, 30% to wants, 20% to savings.",
    "Diversify investments across asset classes to reduce risk.",
    "Automate transfers to savings right after payday to build consistency.",
    "Review recurring subscriptions quarterly to eliminate unused ones.",
])
