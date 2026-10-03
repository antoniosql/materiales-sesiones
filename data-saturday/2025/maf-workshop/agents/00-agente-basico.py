import asyncio
import os

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

from dotenv import load_dotenv


# Configurar el cliente para usa GitHub Models, Ollama o OpenAI
load_dotenv(override=True)

client = OpenAIChatClient(
        base_url=os.getenv("GITHUB_ENDPOINT"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model_id=os.getenv("GITHUB_MODEL", "openai/gpt-4o"),
    )

agent = ChatAgent(chat_client=client, instructions="Eres un agente informativo. Responde a las preguntas con alegría.")


async def main():
    response = await agent.run("¿Qué clima hace hoy en Madrid?")
    print(response.text)
       
if __name__ == "__main__":
    asyncio.run(main())