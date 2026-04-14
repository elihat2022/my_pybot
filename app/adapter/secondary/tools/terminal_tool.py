from app.ports.primary.tools_port import ToolsPort
import subprocess
import platform
from typing import List, Dict, Any

class SystemTerminalAdapter(ToolsPort):
    def __init__(self):
        self.os_name = platform.system().lower()

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
            "function": {
                "name": "execute_terminal_command",
                "description": f"Executes a CLI command. IMPORTANT: The system is running on {self.os_name}. Use appropriate commands (e.g., PowerShell/CMD for Windows, Bash for Mac/Linux).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The command to execute"}
                    },
                    "required": ["command"]
                }
            }
            }
        ]
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        command = arguments.get("command")
        if not command:
            return "Error: No command provided."
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd="."
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            return output if output else "Success: Command executed with no output."
        except Exception as e:
            return f"Critical error executing command: {str(e)}"
