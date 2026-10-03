import asyncio
from agent_framework.observability import setup_observability

# Enable Agent Framework telemetry with console output (default behavior)
setup_observability(enable_sensitive_data=True)

from agent_framework.observability import get_tracer, get_meter

tracer = get_tracer()
meter = get_meter()

with tracer.start_as_current_span("my_custom_span"):
    # Your code here
    pass

counter = meter.create_counter("my_custom_counter")
counter.add(1, {"key": "value"})

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

from dotenv import load_dotenv
load_dotenv()

client = OpenAIChatClient(
        base_url=os.getenv("GITHUB_ENDPOINT"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model_id=os.getenv("GITHUB_MODEL", "openai/gpt-4o"),
    )

# Create the agent - telemetry is automatically enabled
agent = ChatAgent(
    chat_client=client,
    name="Joker",
    instructions="You are good at telling jokes."
)

# Run the agent
result = await agent.run("Tell me a joke about a pirate.")
print(result.text)