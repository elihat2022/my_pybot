from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MemoryPort(ABC):
    @abstractmethod
    def save_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Saves a message for a given session."""
        pass

    @abstractmethod
    def get_message_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns message history for a given session."""
        pass

    @abstractmethod
    def get_last_session_id(self) -> str | None:
        """Returns the latest persisted session id, if any."""
        pass
