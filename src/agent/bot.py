"""LeanBot Agent Engine orchestrating RAG retrieval and response generation."""
import logging
from typing import Dict, Any, List

from src.core.config import settings
from src.core.llm import generate_chat_response
from src.rag.pipeline import RAGPipeline
from src.agent.prompts import build_system_instruction, build_user_prompt
from src.agent.tools.base import ToolRegistry

logger = logging.getLogger(__name__)


class LeanBot:
    """The central conversational AI agent representing EngrLean."""

    def __init__(self, rag_pipeline: RAGPipeline = None, tool_registry: ToolRegistry = None):
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.tool_registry = tool_registry or ToolRegistry()
        self.system_instruction = build_system_instruction()

    def chat_stream(self, user_query: str):
        """Process query and yield streaming response chunks for real-time UI rendering."""
        clean_query = user_query.strip()
        if not clean_query:
            yield "أهلاً بك! كيف يمكنني مساعدتك اليوم في خدمات وتكنولوجيا EngrLean؟"
            return

        # 1. Retrieve knowledge context via RAG
        context, matches = self.rag_pipeline.retrieve_context(clean_query, top_k=settings.rag.top_k)

        # 2. Extract unique source names
        sources = list({m["metadata"].get("source", "Knowledge Base") for m in matches if "metadata" in m})

        # 3. Build augmented user prompt
        prompt = build_user_prompt(clean_query, context)

        # 4. Stream response via Gemini
        from src.core.llm import generate_chat_stream
        for token in generate_chat_stream(prompt, system_instruction=self.system_instruction):
            yield token
        """Process a user query through the RAG pipeline and synthesize a response.
        
        Args:
            user_query: Raw inquiry from the user.
            
        Returns:
            Dictionary containing:
                - reply: The synthesized agent response text.
                - sources: List of source document names used for context.
                - matches: Detailed chunk metadata and distance metrics.
        """
        clean_query = user_query.strip()
        if not clean_query:
            return {
                "reply": "أهلاً بك! كيف يمكنني مساعدتك اليوم في خدمات وتكنولوجيا EngrLean؟",
                "sources": [],
                "matches": [],
            }

        try:
            # 1. Retrieve knowledge context via RAG
            context, matches = self.rag_pipeline.retrieve_context(clean_query, top_k=settings.rag.top_k)

            # 2. Extract unique source names
            sources = list({m["metadata"].get("source", "Knowledge Base") for m in matches if "metadata" in m})

            # 3. Build augmented user prompt
            prompt = build_user_prompt(clean_query, context)

            # 4. Generate response via Gemini 1.5 Flash
            reply_text = generate_chat_response(prompt, system_instruction=self.system_instruction)

            return {
                "reply": reply_text,
                "sources": sources,
                "matches": matches,
            }

        except Exception as e:
            logger.exception(f"Error during LeanBot chat turn: {e}")
            error_details = str(e)
            return {
                "reply": (
                    f"⚠️ **حدث خطأ أثناء الاتصال بالخدمة:**\n\n"
                    f"`{error_details}`\n\n"
                    f"يرجى التأكد من اتصال الإنترنت وصلاحيات المفتاح، أو التواصل مع فريق الدعم عبر:\n"
                    f"• واتساب: {settings.company.support_phone}\n"
                    f"• بريد: {settings.company.support_email}"
                ),
                "sources": [],
                "matches": [],
                "error": error_details,
            }

