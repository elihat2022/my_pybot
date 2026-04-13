from abc import ABC, abstractmethod
from app.domain.model_payload import BotAIModel


class AIProviderPort(ABC):
    @abstractmethod
    async def generate_response(self, ai_model: BotAIModel, message: str):
        pass
    