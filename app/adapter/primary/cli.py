import json
import uuid
import asyncio

from app.adapter.secondary.database.database_adapter import SQLiteMemoryAdapter
from app.ports.primary.ai_provider_port import AIProviderPort
from app.adapter.secondary.openrouter_connection import OpenRouterConnection
from app.domain.model_payload import BotAIModel
from app.adapter.secondary.tools.terminal_tool import SystemTerminalAdapter

async def start_agentic_bot(ai_client: AIProviderPort, terminal_tool: SystemTerminalAdapter, memory_adapter: SQLiteMemoryAdapter):
    print("="*50)
    print("🤖 AI Agent")
    print("="*50)

    # Check for existing session or create new one
    last_session = memory_adapter.get_last_session_id()
    
    if last_session:
        session_id = last_session
        print(f"📡 Resuming Session: {session_id}")
    else:
        session_id = f"bot_sess_{uuid.uuid4().hex[:12]}"
        print(f"📡 New Session ID: {session_id}")
            
    print("="*50)

    ai_model = BotAIModel(tools_schema=terminal_tool.get_tools_schema())
    
    # Load History from DB
    history = memory_adapter.get_message_history(session_id, limit=30)
    for msg in history:
        ai_model.add_message(msg)

    while True:
        prompt = input("\n🧑 You: ")
        if prompt.lower() in ['salir', 'exit', 'quit']:
            break
        if not prompt.strip():
            continue    


        user_message_dict = {"role": "user", "content": prompt}
        memory_adapter.save_message(session_id, user_message_dict)
        ai_model.add_message(user_message_dict)
        
    
        while True:
            print("⏳ [AI is thinking...]") 
            
            response_msg = await ai_client.generate_response(ai_model=ai_model, message=None)
            
            clean_assistant_msg = {
                "role": "assistant",
                "content": response_msg.get("content", "") or ""
            }
            if "tool_calls" in response_msg and response_msg["tool_calls"]:
                clean_tool_calls = []
                for tc in response_msg["tool_calls"]:
                    clean_tool_calls.append({
                        "id": tc.get("id"),
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    })
                clean_assistant_msg["tool_calls"] = clean_tool_calls
           
            memory_adapter.save_message(session_id, clean_assistant_msg)
            ai_model.add_message(clean_assistant_msg)

            if "tool_calls" in response_msg and response_msg["tool_calls"]:
                tool_call = response_msg["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])

                result = terminal_tool.execute_tool(tool_name, arguments)
                print(f"⚙️  [System Result]:\n{result}")
                
             
                tool_result_dict = {
                    "role": "tool",
                    "name": tool_name,
                    "content": str(result),
                    "tool_call_id": tool_call["id"]
                }
                memory_adapter.save_message(session_id, tool_result_dict)
                ai_model.add_message(tool_result_dict)
                
               
            else:
                
                ai_text = response_msg.get("content", "")
                if ai_text:
                    print(f"\n🤖 AI: {ai_text}")
                break

if __name__ == "__main__":
    # --- DEPENDENCY INJECTION ---
    openrouter_client = OpenRouterConnection()
    mac_terminal_tool = SystemTerminalAdapter()
    sqlite_memory_adapter = SQLiteMemoryAdapter(db_path="memory.db")
    try:
        asyncio.run(start_agentic_bot(openrouter_client, mac_terminal_tool, sqlite_memory_adapter))
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
