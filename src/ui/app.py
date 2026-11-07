"""Streamlit Web Presentation Layer for EngrLean Smart RAG Agent."""
import logging
import streamlit as st

from src.core.config import settings
from src.core.secrets import get_gemini_api_key
from src.agent.bot import LeanBot
from src.rag.pipeline import RAGPipeline
from src.ui.styles import ENGRLEAN_CSS

logger = logging.getLogger(__name__)


def get_bot_instance() -> LeanBot:
    """Initialize and store the LeanBot and RAGPipeline instance in session state."""
    if "bot_instance" not in st.session_state:
        pipeline = RAGPipeline()
        st.session_state.bot_instance = LeanBot(rag_pipeline=pipeline)
    return st.session_state.bot_instance


def run_app():
    """Main Streamlit execution loop."""
    st.set_page_config(
        page_title=f"{settings.company.name} — {settings.agent.name}",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject EngrLean Custom Brand CSS
    st.markdown(ENGRLEAN_CSS, unsafe_allow_html=True)

    # 1. Verify API Key Presence
    api_key_valid = True
    try:
        get_gemini_api_key()
    except ValueError as e:
        api_key_valid = False
        st.error(f"⚠️ **Configuration Notice:** {e}")
        st.info(
            "💡 **Streamlit Cloud Deployment:** Add `GEMINI_API_KEY = '...'` into "
            "App Settings -> Secrets."
        )

    # 2. Sidebar: Corporate Profile & Management
    with st.sidebar:
        st.markdown(f"### ⚙️ {settings.company.name}")
        st.markdown(
            f"<div class='status-badge'>CEO: {settings.company.ceo}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"*{settings.company.taglines[0]}*")

        st.markdown("---")
        st.markdown("#### 🏛️ Core Pillars")

        st.markdown(
            """
            <div class='sidebar-pillar-card'>
                <div class='sidebar-pillar-title'>1. Digital Transformation</div>
                <div class='sidebar-pillar-desc'>IT Consulting, Governance, Compliance & Cybersecurity Advisory.</div>
            </div>
            <div class='sidebar-pillar-card'>
                <div class='sidebar-pillar-title'>2. Software & Integration</div>
                <div class='sidebar-pillar-desc'>Custom Enterprise Systems, ERP/CRM, APIs & DevOps.</div>
            </div>
            <div class='sidebar-pillar-card'>
                <div class='sidebar-pillar-title'>3. ICT & Smart Systems</div>
                <div class='sidebar-pillar-desc'>Data Centers, Smart Buildings & Emerging Smart Home Automation.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### 📞 Direct Support & Sales")
        st.markdown(
            f"""
            <a class='contact-btn' href='{settings.company.whatsapp_link}' target='_blank'>💬 Chat on WhatsApp</a>
            <a class='contact-btn' href='mailto:{settings.company.support_email}'>✉️ Email: {settings.company.support_email}</a>
            <a class='contact-btn' href='{settings.company.website}' target='_blank'>🌐 Visit engrlean.com</a>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### ⚡ Knowledge Maintenance")
        if st.button("🔄 Re-index Knowledge Base", use_container_width=True):
            if not api_key_valid:
                st.error("Cannot re-index without a valid GEMINI_API_KEY.")
            else:
                with st.spinner("Re-indexing documents from data/knowledge/..."):
                    try:
                        bot = get_bot_instance()
                        count = bot.rag_pipeline.ingest_all(force_reindex=True)
                        st.success(f"✔ Successfully re-indexed {count} knowledge chunks!")
                    except Exception as ex:
                        st.error(f"Re-indexing failed: {ex}")

    # 3. Main Header Banner
    st.markdown(
        f"""
        <div class='engrlean-header'>
            <div class='engrlean-title'>⚙️ Engr<span>Lean</span> Smart Assistant</div>
            <div class='engrlean-tagline'>"{settings.company.taglines[1]}"</div>
            <div class='engrlean-subtext'>
                Welcome to EngrLean's intelligent engineering & technology advisor. Ask in Arabic or English about our services, pillars, and solutions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Initialize Chat Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    f"مرحباً بك! أنا **{settings.agent.name}**، المستشار الذكي لشركة **{settings.company.name}** "
                    f"تحت قيادة المهندس **{settings.company.ceo}**.\n\n"
                    f"يسعدني مساعدتك في الإجابة عن أي استفسار يخص ركائزنا الهندسية، خدمات التحول الرقمي، "
                    f"البرمجيات، وحلول البنية التحتية والأنظمة الذكية. تفضل بسؤالك!"
                ),
                "sources": [],
            }
        ]

    # 5. Suggested Starter Inquiries
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏢 ما هي ركائز شركة EngrLean؟", use_container_width=True):
            st.session_state.pending_query = "ما هي ركائز ومجالات شركة EngrLean بالتفصيل؟"
    with col2:
        if st.button("🏡 هل تقدمون خدمات المنازل الذكية؟", use_container_width=True):
            st.session_state.pending_query = "هل تقدم شركة EngrLean خدمات المنازل الذكية Smart Home؟"
    with col3:
        if st.button("🌐 What are your software services?", use_container_width=True):
            st.session_state.pending_query = "What custom software and systems integration services do you provide?"

    # 6. Render Existing Chat Transcript
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 Knowledge Sources", expanded=False):
                    for src in msg["sources"]:
                        st.caption(f"• {src}")

    # 7. Process Pending Starter Inquiries or Direct Input
    user_input = st.chat_input("اكتب استفسارك هنا / Type your inquiry here...")

    if hasattr(st.session_state, "pending_query") and st.session_state.pending_query:
        query_to_process = st.session_state.pending_query
        st.session_state.pending_query = None
    elif user_input:
        query_to_process = user_input
    else:
        query_to_process = None

    if query_to_process:
        # Display user message immediately
        st.session_state.messages.append({"role": "user", "content": query_to_process})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        # Generate LeanBot response
        with st.chat_message("assistant"):
            if not api_key_valid:
                error_reply = (
                    "⚠️ لم يتم العثور على مفتاح API صالح. يرجى إدخال `GEMINI_API_KEY` "
                    "في ملف `.env` محلياً أو في `Secrets` على Streamlit Cloud."
                )
                st.markdown(error_reply)
                st.session_state.messages.append({"role": "assistant", "content": error_reply, "sources": []})
            else:
                try:
                    bot = get_bot_instance()
                    # Stream response directly to UI in real-time
                    reply_stream = bot.chat_stream(query_to_process)
                    full_reply = st.write_stream(reply_stream)

                    # Retrieve sources for display
                    _, matches = bot.rag_pipeline.retrieve_context(query_to_process, top_k=settings.rag.top_k)
                    sources = list({m["metadata"].get("source", "Knowledge Base") for m in matches if "metadata" in m})

                    if sources:
                        with st.expander("📚 Knowledge Sources", expanded=False):
                            for s in sources:
                                st.caption(f"• {s}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_reply,
                        "sources": sources,
                    })
                except Exception as err:
                    logger.exception("Failed to generate response in UI.")
                    err_str = str(err)
                    if "429" in err_str or "quota" in err_str.lower() or "resourceexhausted" in err_str.lower():
                        error_msg = (
                            "⏳ **تنبيه استهلاك الحد المؤقت (Rate Limit):**\n\n"
                            "تم تجاوز حد الطلبات المجاني المؤقت في الدقيقة الواحدة على Google AI Studio (مسموح بـ 5-15 طلباً في الدقيقة).\n\n"
                            "👉 **الحل:** انتظر حوالي **20 ثانية** فقط ثم أعد إرسال السؤال وسيجيبك الموديل فوراً."
                        )
                    else:
                        error_msg = (
                            f"⚠️ **حدث خطأ أثناء الاتصال:**\n\n`{err_str}`\n\n"
                            f"يرجى التأكد من اتصال الإنترنت وصلاحيات المفتاح، أو مراجعة الدعم الفني."
                        )
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": [],
                    })

