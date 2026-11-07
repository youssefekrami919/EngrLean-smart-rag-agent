"""Vector Store module encapsulating ChromaDB with Google Gemini Embeddings."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings

from src.core.config import settings
from src.core.llm import generate_embedding
from src.rag.chunker import TextChunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages persistent ChromaDB vector storage and semantic querying."""

    def __init__(self, chroma_dir: Path = settings.chroma_dir, collection_name: str = settings.rag.collection_name):
        self.chroma_dir = chroma_dir
        self.collection_name = collection_name
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "EngrLean corporate knowledge store"}
        )
        logger.info(f"Connected to ChromaDB at '{self.chroma_dir}'. Collection: '{self.collection_name}' (Count: {self.collection.count()})")

    def count(self) -> int:
        """Return total items in the vector collection."""
        return self.collection.count()

    def clear(self) -> None:
        """Delete and recreate the collection for clean re-indexing."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "EngrLean corporate knowledge store"}
            )
            logger.info(f"Cleared vector collection '{self.collection_name}'.")
        except Exception as e:
            logger.warning(f"Error while resetting collection: {e}")

    def add_chunks(self, chunks: List[TextChunk], batch_size: int = 10) -> int:
        """Embed and upsert text chunks into ChromaDB."""
        if not chunks:
            logger.warning("No chunks provided to add_chunks.")
            return 0

        logger.info(f"Generating embeddings and indexing {len(chunks)} chunks...")
        total_indexed = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            ids = [c.chunk_id for c in batch]
            documents = [c.content for c in batch]
            metadatas = [c.metadata for c in batch]

            # Generate embeddings via Google text-embedding-004
            embeddings = []
            for doc in documents:
                emb = generate_embedding(doc, task_type="retrieval_document")
                embeddings.append(emb)

            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            total_indexed += len(batch)
            logger.info(f"Indexed batch {i // batch_size + 1}: {total_indexed}/{len(chunks)} chunks.")

        return total_indexed

    def similarity_search(
        self,
        query: str,
        top_k: int = settings.rag.top_k,
    ) -> List[Dict[str, Any]]:
        """Perform semantic similarity search for a user query."""
        if self.count() == 0:
            logger.warning("Vector store is empty. No documents to search.")
            return []

        query_embedding = generate_embedding(query, task_type="retrieval_query")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.count()),
            include=["documents", "metadatas", "distances"]
        )

        matched_documents: List[Dict[str, Any]] = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc_content, meta, dist in zip(docs, metas, dists):
                matched_documents.append({
                    "content": doc_content,
                    "metadata": meta,
                    "distance": dist,
                })

        return matched_documents

