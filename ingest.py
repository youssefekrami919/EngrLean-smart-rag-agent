"""Standalone CLI Ingestion Script for EngrLean Knowledge Base.

Usage:
    python ingest.py

This script reads all documents from `data/knowledge/`, generates vector embeddings
using Google text-embedding-004, and updates the persistent ChromaDB store.
"""
import sys
import logging
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.core.config import settings
from src.core.secrets import get_gemini_api_key
from src.rag.pipeline import RAGPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("engrlean.ingest")


def main():
    print("=" * 65)
    print(f"🚀 {settings.company.name} Knowledge Base CLI Ingestion Tool")
    print(f"CEO: {settings.company.ceo}")
    print(f"Target Directory: {settings.knowledge_dir}")
    print(f"Vector Database:  {settings.chroma_dir}")
    print("=" * 65)

    try:
        # Validate API Key
        key = get_gemini_api_key()
        masked_key = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"
        print(f"✔ API Key verified: {masked_key}")

        print("\n⏳ Ingesting and embedding documents...")
        pipeline = RAGPipeline()
        count = pipeline.ingest_all(force_reindex=True)

        print("\n" + "=" * 65)
        print(f"✔ Successfully indexed {count} knowledge chunks into ChromaDB.")
        print(f"✔ RAG Knowledge base is up to date and ready for LeanBot queries.")
        print("=" * 65)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Ingestion failed due to an unexpected error.")
        print(f"\n❌ Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

