"""Main Entrypoint for EngrLean Smart RAG Agent Application.

Specifically structured as a single root orchestrator to support seamless deployment
onto Streamlit Community Cloud (via `streamlit run main.py`) without nested path issues,
while keeping presentation strictly decoupled from the core business and RAG logic.
"""
import sys
from pathlib import Path

# Explicitly ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ui.app import run_app

if __name__ == "__main__":
    run_app()

