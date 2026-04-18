from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AIProviderPort(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Returns the model response message using provider-agnostic inputs."""
        pass
