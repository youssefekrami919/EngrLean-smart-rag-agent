"""Text chunking module with recursive character text splitting."""
import re
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from src.core.config import settings
from src.rag.loader import LoadedDocument

logger = logging.getLogger(__name__)


class TextChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def recursive_split_text(
    text: str,
    chunk_size: int = settings.rag.chunk_size,
    chunk_overlap: int = settings.rag.chunk_overlap,
) -> List[str]:
    """Recursively split text into coherent chunks based on natural text separators.
    
    Order of split precedence:
    1. Double newlines (paragraphs)
    2. Single newlines (lines / list items)
    3. Sentence periods / Arabic stops (sentences)
    4. Spaces (words)
    5. Raw character fallback
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    separators = ["\n\n", "\n", ". ", "؟ ", "؛ ", " ", ""]
    
    def _split(txt: str, seps: List[str]) -> List[str]:
        if not seps:
            return [txt]
        
        sep = seps[0]
        splits = txt.split(sep) if sep else list(txt)
        
        chunks = []
        current_chunk = ""
        
        for piece in splits:
            candidate = f"{current_chunk}{sep}{piece}" if current_chunk else piece
            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(piece) > chunk_size:
                    # Recursive split on next separator
                    sub_chunks = _split(piece, seps[1:])
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = piece
                    
        if current_chunk:
            chunks.append(current_chunk)
            
        return [c.strip() for c in chunks if c.strip()]

    raw_chunks = _split(text, separators)
    
    # Merge small chunks with overlap
    final_chunks: List[str] = []
    for i, c in enumerate(raw_chunks):
        if not final_chunks:
            final_chunks.append(c)
        else:
            prev = final_chunks[-1]
            if len(prev) + len(c) < chunk_size:
                final_chunks[-1] = f"{prev}\n{c}"
            else:
                # Add overlap from tail of previous chunk
                if chunk_overlap > 0 and len(prev) > chunk_overlap:
                    overlap_prefix = prev[-chunk_overlap:].strip()
                    final_chunks.append(f"...{overlap_prefix}\n{c}")
                else:
                    final_chunks.append(c)
                    
    return final_chunks


def chunk_documents(
    documents: List[LoadedDocument],
    chunk_size: int = settings.rag.chunk_size,
    chunk_overlap: int = settings.rag.chunk_overlap,
) -> List[TextChunk]:
    """Process a list of LoadedDocuments into indexed TextChunk instances."""
    all_chunks: List[TextChunk] = []

    for doc_idx, doc in enumerate(documents):
        source_name = doc.metadata.get("source", f"doc_{doc_idx}")
        splits = recursive_split_text(doc.content, chunk_size, chunk_overlap)
        
        for split_idx, split_content in enumerate(splits):
            chunk_id = f"{source_name}_chunk_{split_idx}"
            chunk_metadata = {
                **doc.metadata,
                "chunk_id": chunk_id,
                "chunk_index": split_idx,
                "total_chunks_in_doc": len(splits),
            }
            all_chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    content=split_content,
                    metadata=chunk_metadata,
                )
            )

    logger.info(f"Chunking completed. Generated {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks

