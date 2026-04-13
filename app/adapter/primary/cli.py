
from app.ports.primary.ai_provider_port import AIProviderPort
from app.adapter.secondary.openrouter_connection import OpenRouterConnection
from app.domain.model_payload import BotAIModel
import asyncio

async def start_agentic_bot(ai_client: AIProviderPort):
    print("="*50)
    print("🤖 AI Agent")
    print("="*50)

    ai_model = BotAIModel()
    while True:
        prompt = input("\n🧑 You: ")
        if prompt.lower() in ['salir', 'exit', 'quit']:
            break
        if not prompt.strip():
            continue    

        current_prompt = prompt

        while True:
            print("⏳ [AI is thinking...]") 
            response_msg = await ai_client.generate_response(ai_model= ai_model, message=current_prompt)
            current_prompt = None
            ai_text = response_msg.get("content", "")
            print(f"\n🤖 AI: {ai_text}")
            break

if __name__ == "__main__":
    # --- DEPENDENCY INJECTION ---
    openrouter_client = OpenRouterConnection()
    try:
        asyncio.run(start_agentic_bot(openrouter_client))
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")