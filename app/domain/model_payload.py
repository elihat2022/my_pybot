from abc import ABC, abstractmethod
import platform
from typing import List, Dict, Any, Optional

class AIModel(ABC):
    @abstractmethod
    def set_payload(self, message: str)-> dict:
        pass

class BotAIModel(AIModel):
    def __init__(self, tools_schema: Optional[List[Dict[str, Any]]] = None):
        self.tools_schema = tools_schema or []
        self.os_name = platform.system()
        base_prompt = f"You are a helpful assistant. You have access to the user's terminal via the 'execute_terminal_command' tool. The user is currently running {self.os_name}."

        self.history = [
            {
                "role": "system", 
                "content": base_prompt
            }
        ]
    def add_message(self, message:dict):
        self.history.append(message)
    
    def set_payload(self, message):
        if message:
            self.history.append({
                "role": "user",
                "content": message
            })

        payload = {
            "model": "google/gemini-3.1-flash-lite-preview", 
            "temperature": 0.8,
            "messages": self.history
        }

        if self.tools_schema:
            payload["tools"] = self.tools_schema
        return payload