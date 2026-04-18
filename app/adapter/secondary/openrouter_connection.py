
import os
import httpx
import json
from typing import Any, Dict, List, Optional

from app.ports.outbound.ai_provider_port import AIProviderPort

class OpenRouterConnection(AIProviderPort):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = 'https://openrouter.ai/api/v1'
            self.http_client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_key}"})
            self.initialized = True
    
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        payload: Dict[str, Any] = {
            "model": "google/gemini-3.1-flash-lite-preview",
            "temperature": 0.8,
            "messages": messages,
        }
        if config:
            payload.update(config)
        if tools:
            payload["tools"] = tools

        response = await self.http_client.post(f"{self.base_url}/chat/completions", json=payload, timeout=120)
        data = response.json()
        if "choices" not in data:
            print(f"❌ OPENROUTER API ERROR: {json.dumps(data, indent=2)}")
            return {"content": "Error: Could not retrieve response from provider."}
        return data["choices"][0]["message"]
        