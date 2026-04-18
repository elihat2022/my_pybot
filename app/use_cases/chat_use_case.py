import json
import platform
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.ports.inbound.chat_use_case_port import ChatUseCasePort
from app.ports.outbound.ai_provider_port import AIProviderPort
from app.ports.outbound.memory_port import MemoryPort
from app.ports.outbound.tools_port import ToolsPort


class ChatUseCase(ChatUseCasePort):
    def __init__(
        self,
        ai_provider: AIProviderPort,
        memory: MemoryPort,
        tools: List[ToolsPort],
        model_config: Optional[Dict[str, Any]] = None,
        history_limit: int = 30,
    ):
        self.ai_provider = ai_provider
        self.memory = memory
        self.tools = tools
        self.model_config = model_config or {
            "model": "google/gemini-3.1-flash-lite-preview",
            "temperature": 0.8,
        }
        self.history_limit = history_limit

        self.tools_schema: List[Dict[str, Any]] = []
        for tool_adapter in self.tools:
            self.tools_schema.extend(tool_adapter.get_tools_schema())

        self.session_id = self.memory.get_last_session_id() or f"bot_sess_{uuid.uuid4().hex[:12]}"
        self.history: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "You have access to tools described in the tools schema. "
                    f"The user is currently running {platform.system()}, "
                    f"today is {datetime.now().strftime('%Y-%m-%d')}."
                ),
            }
        ]

        previous_messages = self.memory.get_message_history(self.session_id, limit=self.history_limit)
        self.history.extend(previous_messages)

    def get_session_id(self) -> str:
        return self.session_id

    async def handle_user_input(self, user_input: str) -> Dict[str, Any]:
        if not user_input.strip():
            return {"assistant_response": "", "tool_results": []}

        user_message = {"role": "user", "content": user_input}
        self.memory.save_message(self.session_id, user_message)
        self.history.append(user_message)

        tool_results: List[Dict[str, str]] = []

        while True:
            response_msg = await self.ai_provider.generate_response(
                messages=self.history,
                tools=self.tools_schema,
                config=self.model_config,
            )

            clean_assistant_msg = {
                "role": "assistant",
                "content": response_msg.get("content", "") or "",
            }

            if response_msg.get("tool_calls"):
                normalized_calls: List[Dict[str, Any]] = []
                for tool_call in response_msg["tool_calls"]:
                    normalized_calls.append(
                        {
                            "id": tool_call.get("id"),
                            "type": tool_call.get("type", "function"),
                            "function": {
                                "name": tool_call["function"]["name"],
                                "arguments": tool_call["function"]["arguments"],
                            },
                        }
                    )
                clean_assistant_msg["tool_calls"] = normalized_calls

            self.memory.save_message(self.session_id, clean_assistant_msg)
            self.history.append(clean_assistant_msg)

            if not response_msg.get("tool_calls"):
                return {
                    "assistant_response": clean_assistant_msg["content"],
                    "tool_results": tool_results,
                }

            for tool_call in response_msg["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = self._parse_tool_arguments(tool_call["function"].get("arguments", "{}"))

                result = await self._execute_tool_call(tool_name, tool_args)
                tool_results.append({"name": tool_name, "result": result})

                tool_message = {
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result),
                    "tool_call_id": tool_call.get("id"),
                }
                self.memory.save_message(self.session_id, tool_message)
                self.history.append(tool_message)

    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        for tool_adapter in self.tools:
            if tool_adapter.supports_tool(tool_name):
                return await tool_adapter.execute_tool(tool_name, arguments)
        return f"Error: Tool {tool_name} not found."

    @staticmethod
    def _parse_tool_arguments(raw_arguments: Any) -> Dict[str, Any]:
        if isinstance(raw_arguments, dict):
            return raw_arguments
        if isinstance(raw_arguments, str):
            try:
                parsed = json.loads(raw_arguments)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        return {}
