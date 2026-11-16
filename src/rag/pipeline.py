"""RAG Pipeline — Hybrid: In-Memory Direct Context + Optional Vector Search.

For small knowledge bases (MVP stage), documents are loaded once into RAM and
injected directly into the LLM prompt. This eliminates all network calls for
embeddings and delivers sub-second response times.

When the knowledge base grows beyond the LLM context window, the vector search
path activates automatically.
"""
import logging
from typing import Tuple, List, Dict, Any

from src.core.config import settings
from src.rag.loader import load_knowledge_documents, LoadedDocument

logger = logging.getLogger(__name__)

# In-memory document cache — loaded once, reused for every query
_cached_documents: List[LoadedDocument] = []
_cache_loaded: bool = False

# Threshold: if total knowledge text is under this many characters,
# use Direct Context Injection (no embedding needed).
# ~100K chars ≈ ~25K tokens — well within Gemini 3.8 Flash's 1M token window.
DIRECT_INJECTION_CHAR_LIMIT = 100_000


def _load_and_cache_documents() -> List[LoadedDocument]:
    """Load knowledge documents into memory (once per application lifecycle)."""
    global _cached_documents, _cache_loaded
    if not _cache_loaded:
        _cached_documents = load_knowledge_documents(settings.knowledge_dir)
        _cache_loaded = True
        total_chars = sum(len(d.content) for d in _cached_documents)
        logger.info(
            f"Knowledge cache loaded: {len(_cached_documents)} documents, "
            f"{total_chars:,} total characters."
        )
    return _cached_documents


def invalidate_cache() -> None:
    """Force reload of knowledge documents on next query (used after re-indexing)."""
    global _cached_documents, _cache_loaded
    _cached_documents = []
    _cache_loaded = False
    logger.info("Knowledge cache invalidated. Will reload on next query.")


class RAGPipeline:
    """High-level orchestrator for knowledge retrieval.

    Uses pre-computed ChromaDB vector similarity search directly from disk.
    Falls back gracefully to cached documents if needed.
    """

    def __init__(self):
        try:
            from src.rag.vectorstore import VectorStore
            self._vector_store = VectorStore()
            # Auto-bootstrap safeguard: If the store exists but is empty, index once automatically
            if self._vector_store.count() == 0:
                logger.info("Vector database is empty. Auto-bootstrapping from data/knowledge/...")
                self._run_ingestion()
        except Exception as e:
            logger.warning(f"VectorStore pre-connect notice: {e}")
            self._vector_store = None

    def retrieve_context(self, query: str, top_k: int = settings.rag.top_k) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant context for a user query.

        Prioritizes semantic vector similarity search from the pre-computed ChromaDB store.
        Does NOT re-index or re-compute document vectors at runtime.
        Falls back to cached documents only if vector store is unavailable.
        """
        try:
            if self._vector_store is None:
                from src.rag.vectorstore import VectorStore
                self._vector_store = VectorStore()

            if self._vector_store.count() > 0:
                matches = self._vector_store.similarity_search(query, top_k=top_k)
                if matches:
                    context_blocks = []
                    for i, match in enumerate(matches, 1):
                        src = match["metadata"].get("source", "Knowledge Base")
                        context_blocks.append(
                            f"--- Context #{i} [Source: {src}] ---\n{match['content']}"
                        )
                    return "\n\n".join(context_blocks), matches
        except Exception as e:
            logger.warning(f"Vector search notice ({e}). Falling back to cached documents.")

        # Fallback to cached documents if vector store is empty or unavailable
        documents = _load_and_cache_documents()
        return self._direct_context(documents) if documents else ("", [])

    def _direct_context(self, documents: List[LoadedDocument]) -> Tuple[str, List[Dict[str, Any]]]:
        """Inject all documents directly into the prompt context (instant)."""
        context_blocks = []
        sources = []
        for i, doc in enumerate(documents, 1):
            src_name = doc.metadata.get("source", "Knowledge Document")
            context_blocks.append(
                f"--- Document #{i} [Source: {src_name}] ---\n{doc.content}"
            )
            sources.append({"content": doc.content, "metadata": doc.metadata})

        return "\n\n".join(context_blocks), sources

    def _vector_context(self, query: str, top_k: int) -> Tuple[str, List[Dict[str, Any]]]:
        """Use ChromaDB vector similarity search for large corpora."""
        try:
            if self._vector_store is None:
                from src.rag.vectorstore import VectorStore
                self._vector_store = VectorStore()

            if self._vector_store.count() == 0:
                self._run_ingestion()

            matches = self._vector_store.similarity_search(query, top_k=top_k)
            if matches:
                context_blocks = []
                for i, match in enumerate(matches, 1):
                    src = match["metadata"].get("source", "Knowledge Base")
                    context_blocks.append(
                        f"--- Context #{i} [Source: {src}] ---\n{match['content']}"
                    )
                return "\n\n".join(context_blocks), matches
        except Exception as e:
            logger.warning(f"Vector search failed ({e}). Falling back to direct context.")

        # Fallback to direct context injection
        documents = _load_and_cache_documents()
        return self._direct_context(documents) if documents else ("", [])

    def _run_ingestion(self) -> int:
        """Index documents into vector store."""
        from src.rag.chunker import chunk_documents
        documents = _load_and_cache_documents()
        if not documents:
            return 0
        chunks = chunk_documents(documents)
        try:
            return self._vector_store.add_chunks(chunks)
        except Exception as e:
            logger.warning(f"Vector store add_chunks warning ({e}). Documents are cached in memory.")
            return len(chunks)

    def ingest_all(self, force_reindex: bool = True) -> int:
        """Public method: Re-index knowledge base and invalidate cache."""
        invalidate_cache()
        documents = _load_and_cache_documents()
        if not documents:
            return 0

        from src.rag.chunker import chunk_documents
        chunks = chunk_documents(documents)

        try:
            if self._vector_store is None:
                from src.rag.vectorstore import VectorStore
                self._vector_store = VectorStore()
            if force_reindex:
                self._vector_store.clear()
            self._vector_store.add_chunks(chunks)
        except Exception as e:
            logger.warning(f"Vector indexing notice ({e}). Knowledge is fully active via in-memory direct cache.")

        return len(chunks)
