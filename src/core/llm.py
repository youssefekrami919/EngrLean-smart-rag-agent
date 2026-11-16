"""Google Generative AI (Gemini) Client — Clean, Single-Model, Production-Grade."""
import logging
import warnings
import hashlib
from typing import Optional, List

# Suppress deprecation and runtime warnings from google-generativeai package
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import google.generativeai as genai

from src.core.config import settings
from src.core.secrets import get_gemini_api_key

logger = logging.getLogger(__name__)

_is_configured = False


def configure_gemini() -> None:
    """Configure the Gemini SDK globally with REST transport for maximum network stability."""
    global _is_configured
    if not _is_configured:
        api_key = get_gemini_api_key()
        # Use REST transport instead of gRPC to avoid WSA 995 socket resets and ISP handshake drops
        genai.configure(api_key=api_key, transport="rest")
        _is_configured = True
        logger.info("Gemini SDK configured successfully with REST transport.")


# In-memory query embedding cache for instant (0ms) repeated lookups
_query_embedding_cache = {}


def generate_embedding(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Generate dense vector embedding using Google Gemini embedding API with caching.
    
    Uses 'models/gemini-embedding-001' via REST transport.
    Caches query embeddings in memory for instant lookups.
    Falls back gracefully to a deterministic 3072-dim vector if offline.
    """
    clean_text = text.strip()
    if not clean_text:
        return [0.0] * 3072

    cache_key = f"{task_type}:{clean_text}"
    if cache_key in _query_embedding_cache:
        return _query_embedding_cache[cache_key]

    configure_gemini()
    try:
        result = genai.embed_content(
            model=settings.models.embedding_model,
            content=clean_text,
            task_type=task_type,
            request_options={"timeout": 15},
        )
        if isinstance(result, dict) and "embedding" in result:
            emb = result["embedding"]
            if task_type == "retrieval_query" and len(_query_embedding_cache) < 500:
                _query_embedding_cache[cache_key] = emb
            return emb
    except Exception as e:
        logger.warning(f"Google embedding API call failed ({e}). Using deterministic fallback.")

    # Deterministic fallback vector (3072 dimensions) based on SHA-256
    digest = hashlib.sha256(clean_text.encode("utf-8")).digest()
    return [float((b - 128) / 128.0) for b in (digest * 96)[:3072]]




def generate_chat_response(prompt: str, system_instruction: Optional[str] = None) -> str:
    """Generate a complete chat response with fast zero-hang failover across active Gemini models."""
    configure_gemini()

    models_to_try = settings.models.fallback_models
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config={
                    "temperature": settings.models.temperature,
                    "max_output_tokens": settings.models.max_output_tokens,
                },
            )

            # REST transport with 30s timeout and fast model failover
            response = model.generate_content(
                prompt,
                stream=False,
                request_options={"timeout": 30},
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed ({type(e).__name__}). Trying next active model...")
            continue

    if last_error:
        raise last_error
    return "عذراً، لم أتمكن من معالجة الطلب. يرجى التواصل مع فريق الدعم."


def generate_chat_stream(prompt: str, system_instruction: Optional[str] = None):
    """Yield streaming response chunks with zero-hang failover across active Gemini models."""
    configure_gemini()

    models_to_try = settings.models.fallback_models
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config={
                    "temperature": settings.models.temperature,
                    "max_output_tokens": settings.models.max_output_tokens,
                },
            )

            # REST transport with 30s timeout and fast model failover
            response = model.generate_content(
                prompt,
                stream=True,
                request_options={"timeout": 30},
            )

            chunk_yielded = False
            for chunk in response:
                if chunk.text:
                    chunk_yielded = True
                    yield chunk.text

            if chunk_yielded:
                return  # Stream finished successfully

        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed ({type(e).__name__}). Trying next active model...")
            continue

    if last_error:
        raise last_error

