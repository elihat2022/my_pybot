from abc import ABC, abstractmethod
import platform


class AIModel(ABC):
    @abstractmethod
    def set_payload(self, message: str)-> dict:
        pass

class BotAIModel(AIModel):
    def __init__(self):
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
            "model": "minimax/minimax-m2.7",
            "temperature": 0.8,
            "messages": self.history
        }
        return payload