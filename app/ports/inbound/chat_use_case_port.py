from abc import ABC, abstractmethod
from typing import Any, Dict


class ChatUseCasePort(ABC):
    @abstractmethod
    def get_session_id(self) -> str:
        """Returns the active chat session identifier."""
        pass

    @abstractmethod
    async def handle_user_input(self, user_input: str) -> Dict[str, Any]:
        """Processes user input and returns assistant output plus tool execution results."""
        pass
