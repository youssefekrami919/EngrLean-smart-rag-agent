"""Google Generative AI (Gemini) Client & Embedding Wrapper."""
import time
import logging
import warnings
from typing import List, Optional

# Suppress deprecation warnings from google-generativeai package
warnings.filterwarnings("ignore", category=FutureWarning, module="google")

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from src.core.config import settings
from src.core.secrets import get_gemini_api_key

logger = logging.getLogger(__name__)

_is_configured = False


def configure_gemini() -> None:
    """Configure the Gemini SDK globally with the retrieved API key."""
    global _is_configured
    if not _is_configured:
        api_key = get_gemini_api_key()
        genai.configure(api_key=api_key)
        _is_configured = True
        logger.info("Google Generative AI SDK successfully configured.")


def get_gemini_client():
    """Ensure Gemini SDK is configured and return module."""
    configure_gemini()
    return genai


CANDIDATE_EMBED_MODELS = [
    "models/gemini-embedding-001",
    "gemini-embedding-001",
    "models/embedding-001",
    "embedding-001",
    "models/text-embedding-004",
    "text-embedding-004",
]

_active_embed_model: Optional[str] = None


def generate_embedding(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Generate dense vector embedding with resilient model fallback.
    
    Args:
        text: Input string to embed.
        task_type: 'retrieval_document' for indexed chunks, or 'retrieval_query' for user queries.
        
    Returns:
        List of floats representing the embedding vector.
    """
    global _active_embed_model
    configure_gemini()
    clean_text = text.strip()
    if not clean_text:
        return [0.0] * 768

    # If we already identified a working model, try it first
    models_to_try = [_active_embed_model] if _active_embed_model else []
    for m in CANDIDATE_EMBED_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        try:
            # First try with task_type
            try:
                result = genai.embed_content(
                    model=model_name,
                    content=clean_text,
                    task_type=task_type,
                )
            except Exception:
                # Some versions/models only accept plain embedContent without task_type
                result = genai.embed_content(
                    model=model_name,
                    content=clean_text,
                )

            if result and "embedding" in result:
                if _active_embed_model != model_name:
                    logger.info(f"✔ Successfully bound active embedding model: {model_name}")
                    _active_embed_model = model_name
                return result["embedding"]
        except Exception as e:
            last_error = e
            logger.warning(f"Embedding model '{model_name}' failed: {e}. Trying next candidate...")
            continue

    # If all candidates failed, raise the last encountered error
    raise last_error or RuntimeError("All candidate embedding models failed.")


def get_chat_model() -> str:
    """Return the designated Gemini 3.8 Flash model."""
    return "models/gemini-3.8-flash"


def generate_chat_response(prompt: str, system_instruction: Optional[str] = None) -> str:
    """Generate chat response using Gemini 3.8 Flash.
    
    Args:
        prompt: User prompt augmented with context.
        system_instruction: System prompt defining persona and guardrails.
        
    Returns:
        Generated response string.
    """
    configure_gemini()
    generation_config = {
        "temperature": settings.models.temperature,
        "max_output_tokens": settings.models.max_output_tokens,
    }

    model = genai.GenerativeModel(
        model_name="models/gemini-3.8-flash",
        system_instruction=system_instruction,
        generation_config=generation_config,
    )

    try:
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
        return "عذراً، لم أتمكن من معالجة الطلب في الوقت الحالي. يرجى التواصل مع فريق الدعم."
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower() or "resourceexhausted" in err_str.lower():
            raise RuntimeError(
                "تم تجاوز حد الطلبات المجانية المؤقت لـ Gemini 3.8 Flash (5 طلبات/دقيقة).\n"
                "يرجى الانتظار حوالي 20 ثانية ثم إعادة المحاولة."
            ) from e
        raise


def generate_chat_stream(prompt: str, system_instruction: Optional[str] = None):
    """Generate streaming chat response using Gemini 3.8 Flash for ultra-low perceived latency."""
    configure_gemini()
    generation_config = {
        "temperature": settings.models.temperature,
        "max_output_tokens": settings.models.max_output_tokens,
    }

    model = genai.GenerativeModel(
        model_name="models/gemini-3.8-flash",
        system_instruction=system_instruction,
        generation_config=generation_config,
    )

    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower() or "resourceexhausted" in err_str.lower():
            raise RuntimeError(
                "تم تجاوز حد الطلبات المجانية المؤقت لـ Gemini 3.8 Flash (5 طلبات/دقيقة).\n"
                "يرجى الانتظار حوالي 20 ثانية ثم إعادة المحاولة."
            ) from e
        raise
