from typing import List, Dict, Any
from app.ports.outbound.tools_port import ToolsPort
import os

from browser_use_sdk.v3 import AsyncBrowserUse

from dotenv import load_dotenv

load_dotenv()


class BrowserToolAdapter(ToolsPort):

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
            "function": {
                "name": "browse_web",
                "description": f"Browse the web search updated information, interact with web pages, or read documentation, describe what do you want to do or what actions you want to perform on the web.",
                "parameters": {
                    "type": "object",
                    "properties": {
                       "task_prompt": {
                                "type": "string", 
                                "description": "detailed instructions for the browser (e.g., 'Go to wikipedia.org, search for Python and return the first paragraph')"
                            }
                    },
                    "required": ["task_prompt"]
                }
            }
            }
        ]

    def supports_tool(self, tool_name: str) -> bool:
        return tool_name == "browse_web"
    

    async def execute_tool(self, tool_name, arguments):
        if not self.supports_tool(tool_name):
            return "Error: Tool not recognized by this adapter."

        task_prompt = arguments.get("task_prompt")
        if not task_prompt:
            return "Error: No task was provided for the browser."

        try:
            result = await self._run_browser_task(task_prompt)
            return result
        except Exception as e:
            return f"Critical error while running browser task: {str(e)}"

    async def _run_browser_task(self, task_prompt: str) -> str:
        client = AsyncBrowserUse(api_key=os.getenv("BROWSER_USE_API_KEY"))
        result = await client.run(task_prompt)
        return  result.output
    
