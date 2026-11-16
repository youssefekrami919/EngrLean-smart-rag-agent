"""LeanBot Agent — Clean conversational engine with single-pass streaming."""
import logging
from typing import Dict, Any, Generator

from src.core.config import settings
from src.core.llm import generate_chat_stream
from src.rag.pipeline import RAGPipeline
from src.agent.prompts import build_system_instruction, build_user_prompt

logger = logging.getLogger(__name__)


class LeanBot:
    """The central conversational AI agent representing EngrLean."""

    def __init__(self, rag_pipeline: RAGPipeline = None):
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.system_instruction = build_system_instruction()

    def chat(self, user_query: str) -> Dict[str, Any]:
        """Process a query and return a complete response (non-streaming)."""
        from src.core.llm import generate_chat_response

        clean_query = user_query.strip()
        if not clean_query:
            return self._empty_greeting()

        try:
            context, matches = self.rag_pipeline.retrieve_context(clean_query)
            sources = self._extract_sources(matches)
            prompt = build_user_prompt(clean_query, context)
            reply = generate_chat_response(prompt, system_instruction=self.system_instruction)
            return {"reply": reply, "sources": sources, "matches": matches}
        except Exception as e:
            return self._handle_error(e)

    def chat_stream_with_sources(self, user_query: str) -> Dict[str, Any]:
        """Retrieve context ONCE, then return sources + a streaming generator.

        Returns:
            Dict with:
                - "stream": Generator yielding response text chunks
                - "sources": List of source document names
        """
        clean_query = user_query.strip()
        if not clean_query:
            def empty_gen():
                yield "أهلاً بك! كيف يمكنني مساعدتك اليوم في خدمات وتكنولوجيا EngrLean؟"
            return {"stream": empty_gen(), "sources": []}

        # Single retrieval — no duplication
        context, matches = self.rag_pipeline.retrieve_context(clean_query)
        sources = self._extract_sources(matches)
        prompt = build_user_prompt(clean_query, context)

        def stream_gen():
            yield from generate_chat_stream(prompt, system_instruction=self.system_instruction)

        return {"stream": stream_gen(), "sources": sources}

    @staticmethod
    def _extract_sources(matches) -> list:
        """Extract unique source names from match metadata."""
        return list({
            m["metadata"].get("source", "Knowledge Base")
            for m in matches if isinstance(m, dict) and "metadata" in m
        })

    @staticmethod
    def _empty_greeting() -> Dict[str, Any]:
        return {
            "reply": "أهلاً بك! كيف يمكنني مساعدتك اليوم في خدمات وتكنولوجيا EngrLean؟",
            "sources": [],
            "matches": [],
        }

    @staticmethod
    def _handle_error(e: Exception) -> Dict[str, Any]:
        logger.exception(f"LeanBot error: {e}")
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower():
            reply = (
                "⏳ تم تجاوز حد الطلبات المؤقت. يرجى الانتظار 20 ثانية وإعادة المحاولة."
            )
        else:
            reply = (
                f"⚠️ حدث خطأ أثناء الاتصال:\n\n`{err_str}`\n\n"
                f"يرجى التواصل مع فريق الدعم:\n"
                f"• واتساب: {settings.company.support_phone}\n"
                f"• بريد: {settings.company.support_email}"
            )
        return {"reply": reply, "sources": [], "matches": [], "error": err_str}
