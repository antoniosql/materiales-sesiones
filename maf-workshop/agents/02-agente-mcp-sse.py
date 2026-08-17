import asyncio
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient

import os
from dotenv import load_dotenv

load_dotenv()

async def http_mcp_example():
    """Example using an HTTP-based MCP server."""
    async with (
       
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            headers={"Authorization": "Bearer your-token"},
        ) as mcp_server,
        ChatAgent(
            chat_client=OpenAIChatClient(
        base_url=os.getenv("GITHUB_ENDPOINT"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model_id=os.getenv("GITHUB_MODEL", "openai/gpt-4o"),
    ),
            name="DocsAgent",
            instructions="You help with Microsoft documentation questions.",
        ) as agent,
    ):
        result = await agent.run(
            "How to create an Azure storage account using az cli?",
            tools=mcp_server
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(http_mcp_example())