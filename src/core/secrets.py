"""Unified Secrets and Environment Variables Manager.

Seamlessly supports:
1. Streamlit Community Cloud (via st.secrets in TOML format)
2. Local Development (via .env file and os.environ)
"""
import os
from pathlib import Path

# Pre-load local .env if available
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"

try:
    from dotenv import load_dotenv
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)
    else:
        load_dotenv(override=False)
except ImportError:
    # Graceful fallback: manually parse .env if python-dotenv is not installed
    if _env_path.exists():
        try:
            with open(_env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from Streamlit secrets (if available) or environment variables."""
    # 1. Attempt to retrieve from Streamlit Secrets (for Streamlit Community Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        # Streamlit not initialized or not in a Streamlit context
        pass

    # 2. Attempt to retrieve from OS environment / .env
    val = os.getenv(key, default)
    return str(val).strip() if val else default


def get_gemini_api_key() -> str:
    """Retrieve the Google Gemini API key or raise an actionable error."""
    key = get_secret("GEMINI_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not configured!\n\n"
            "- For Local Development: Add your API key to the '.env' file: GEMINI_API_KEY=AIza...\n"
            "- For Streamlit Cloud: Add your API key to App Settings -> Secrets in TOML format:\n"
            '  GEMINI_API_KEY = "AIza..."\n\n'
            "Get your free key at: https://aistudio.google.com/apikey"
        )
    return key
