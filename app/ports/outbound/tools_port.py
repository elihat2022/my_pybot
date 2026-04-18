from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ToolsPort(ABC):
    @abstractmethod
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Returns the JSON schema describing tools exposed to the model."""
        pass

    @abstractmethod
    def supports_tool(self, tool_name: str) -> bool:
        """Indicates whether this adapter can execute the given tool name."""
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Executes a tool call and returns the output as text."""
        pass
