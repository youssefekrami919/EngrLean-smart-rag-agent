"""UI Presentation package for EngrLean."""

def run_app():
    """Lazy loader for Streamlit UI entrypoint."""
    from src.ui.app import run_app as _run_app
    return _run_app()

__all__ = ["run_app"]
