import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.adapter.secondary.database.database_adapter import SQLiteMemoryAdapter
from app.adapter.secondary.openrouter_connection import OpenRouterConnection
from app.adapter.secondary.tools.terminal_tool import SystemTerminalAdapter
from app.adapter.secondary.tools.browser_tool import BrowserToolAdapter
from app.use_cases.chat_use_case import ChatUseCase
from app.ports.inbound.chat_use_case_port import ChatUseCasePort

async def start_agentic_bot(chat_use_case: ChatUseCasePort):
    print("="*50)
    print("🤖 AI Agent")
    print("="*50)
    print(f"📡 Active Session: {chat_use_case.get_session_id()}")
    print("="*50)

    while True:
        prompt = input("\n🧑 You: ")
        if prompt.lower() in ['salir', 'exit', 'quit']:
            break
        if not prompt.strip():
            continue

        print("⏳ [AI is thinking...]")
        result = await chat_use_case.handle_user_input(prompt)

        for tool_result in result.get("tool_results", []):
            print(f"⚙️  [System Result] ({tool_result['name']}):\n{tool_result['result']}")

        ai_text = result.get("assistant_response", "")
        if ai_text:
            print(f"\n🤖 AI: {ai_text}")

if __name__ == "__main__":
    # --- DEPENDENCY INJECTION ---
    openrouter_client = OpenRouterConnection()
    terminal_tool = SystemTerminalAdapter()
    browser_tool = BrowserToolAdapter()  
    sqlite_memory_adapter = SQLiteMemoryAdapter(db_path="memory.db")
    chat_use_case = ChatUseCase(
        ai_provider=openrouter_client,
        memory=sqlite_memory_adapter,
        tools=[terminal_tool, browser_tool],
    )
    try:
        asyncio.run(start_agentic_bot(chat_use_case))
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
