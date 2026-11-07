"""Document loader module for the EngrLean knowledge repository."""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from src.core.config import settings

logger = logging.getLogger(__name__)


class LoadedDocument(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def load_knowledge_documents(knowledge_dir: Path = settings.knowledge_dir) -> List[LoadedDocument]:
    """Scan and load all markdown and text documents from the knowledge directory.
    
    Args:
        knowledge_dir: Path to the directory containing corporate knowledge files.
        
    Returns:
        List of LoadedDocument instances.
    """
    documents: List[LoadedDocument] = []
    
    if not knowledge_dir.exists():
        logger.warning(f"Knowledge directory '{knowledge_dir}' does not exist. Creating it.")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        return documents

    supported_extensions = {".md", ".txt", ".json"}
    
    for file_path in knowledge_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    doc = LoadedDocument(
                        content=text,
                        metadata={
                            "source": str(file_path.name),
                            "file_path": str(file_path.relative_to(settings.root_dir)),
                            "extension": file_path.suffix.lower(),
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Loaded document: {file_path.name} ({len(text)} chars)")
            except Exception as e:
                logger.error(f"Failed to read document {file_path}: {e}")

    logger.info(f"Total documents loaded from knowledge directory: {len(documents)}")
    return documents

