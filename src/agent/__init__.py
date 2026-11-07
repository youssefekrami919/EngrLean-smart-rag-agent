"""Autonomous Agent package for EngrLean."""
from src.agent.prompts import build_system_instruction, build_user_prompt
from src.agent.tools.base import AbstractTool, ToolRegistry

__all__ = [
    "build_system_instruction",
    "build_user_prompt",
    "AbstractTool",
    "ToolRegistry",
]

try:
    from src.agent.bot import LeanBot
    __all__.append("LeanBot")
except ImportError:
    pass
