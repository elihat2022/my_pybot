from abc import ABC, abstractmethod
from typing import List, Dict, Any


class MemoryPort(ABC):
    @abstractmethod
    def save_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        Saves a message to the memory storage for a given session.
        """
        pass
    @abstractmethod
    def get_message_history(self, session_id: str, limit:int =20 ) -> List[Dict[str, Any]]:
        """
        Retrieves the message history for a given session.
        """
        pass