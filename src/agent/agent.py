import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a research and task execution assistant.
Be direct, precise, and helpful. When you don't know something, say so
clearly."""

def run_agent(user_input: str) -> str:
    """The simplest possible agentic loop."""
    messages = [{"role": "user", "content": user_input}]

    # For now, our loop has single iteration
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
        
    return response.content[0].text