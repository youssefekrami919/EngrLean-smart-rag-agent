"""End-to-End RAG Pipeline Orchestrator with Self-Bootstrapping."""
import logging
from typing import Tuple, List, Dict, Any

from src.core.config import settings
from src.rag.loader import load_knowledge_documents
from src.rag.chunker import chunk_documents
from src.rag.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """High-level orchestrator for loading, indexing, and retrieving knowledge."""

    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()

    def ensure_initialized(self) -> None:
        """Self-bootstrapping hook: Ensures vector store has data on startup."""
        try:
            doc_count = self.vector_store.count()
            if doc_count == 0:
                logger.info("Vector database is empty. Triggering automatic self-bootstrapping...")
                self.ingest_all(force_reindex=False)
            else:
                logger.info(f"Vector database verified. Ready with {doc_count} indexed chunks.")
        except Exception as e:
            logger.warning(f"Self-bootstrapping vector store encountered an issue: {e}")

    def ingest_all(self, force_reindex: bool = True) -> int:
        """Read knowledge directory, split chunks, and index into ChromaDB."""
        logger.info(f"Starting ingestion from: {settings.knowledge_dir}")
        documents = load_knowledge_documents(settings.knowledge_dir)
        if not documents:
            logger.warning("No knowledge documents found to index.")
            return 0

        chunks = chunk_documents(
            documents,
            chunk_size=settings.rag.chunk_size,
            chunk_overlap=settings.rag.chunk_overlap,
        )

        if force_reindex:
            self.vector_store.clear()

        indexed_count = self.vector_store.add_chunks(chunks)
        logger.info(f"Ingestion finished successfully. Total indexed chunks: {indexed_count}")
        return indexed_count

    def retrieve_context(self, query: str, top_k: int = settings.rag.top_k) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant context string and source metadata for a user query.
        
        Attempts vector similarity search first. If vector database or embedding
        services are unavailable (e.g. 404 model errors or network glitches),
        seamlessly falls back to Direct Knowledge Injection (reading documents directly)
        leveraging Gemini 1.5 Flash's 1M token context window without interruption.
        """
        try:
            self.ensure_initialized()
            matches = self.vector_store.similarity_search(query, top_k=top_k)
            if matches:
                context_blocks = []
                for i, match in enumerate(matches, 1):
                    source = match["metadata"].get("source", "Knowledge Base")
                    content = match["content"]
                    context_blocks.append(f"--- Document Context #{i} [Source: {source}] ---\n{content}")
                return "\n\n".join(context_blocks), matches
        except Exception as e:
            logger.warning(f"Vector retrieval degraded ({e}). Engaging Direct Knowledge Context Injection...")

        # Bulletproof Fallback: Direct Knowledge Injection from data/knowledge/
        documents = load_knowledge_documents(settings.knowledge_dir)
        if not documents:
            return "", []

        context_blocks = []
        fallback_matches = []
        for i, doc in enumerate(documents, 1):
            src = doc.metadata.get("source", "Knowledge Document")
            context_blocks.append(f"--- Document #{i} [Source: {src}] ---\n{doc.content}")
            fallback_matches.append({"content": doc.content, "metadata": doc.metadata})

        return "\n\n".join(context_blocks), fallback_matches

