"""Abstract Base Tool definition and Registry for modular agent extensibility."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class AbstractTool(ABC):
    """Abstract base class for all pluggable LeanBot execution tools.
    
    Any future capability (e.g., Gmail API notification dispatch, WhatsApp Webhooks,
    CRM connectors) inherits from this class and registers with the ToolRegistry.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool logic and return a structured dictionary."""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Return the function schema representation for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
        }


class ToolRegistry:
    """Registry maintaining available tools for the conversational agent."""

    def __init__(self):
        self._tools: Dict[str, AbstractTool] = {}

    def register(self, tool: AbstractTool) -> None:
        """Register a new tool instance."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} - {tool.description}")

    def get(self, name: str) -> Optional[AbstractTool]:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List metadata for all active tools."""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """Safely execute a registered tool."""
        tool = self.get(name)
        if not tool:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        return tool.execute(**kwargs)

