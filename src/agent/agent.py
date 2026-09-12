import anthropic
import openai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()

client = anthropic.Anthropic()
openai_client = openai.OpenAI()

console = Console()

STEP_STYLES = {
    "THINKING": "cyan",
    "ACTION": "yellow",
    "RESULT": "green",
}

SYSTEM_PROMPT = """You are a research and task execution assistant.
Be direct, precise, and helpful. When you don't know something, say so
clearly. Always structure your responses using bullet points (-)"""


def _debug_step(debug: bool, step_type: str, content: str) -> None:
    """Print a colorized panel for a step of the agentic loop, if debug mode is on."""
    if not debug:
        return
    console.print(Panel(content, title=f"[{step_type}]", border_style=STEP_STYLES.get(step_type, "white")))


def _call_claude(messages: list[dict]) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _call_openai(messages: list[dict]) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
    )
    return response.choices[0].message.content


def run_agent(user_input: str, debug: bool = False) -> str:
    """The simplest possible agentic loop."""
    messages = [{"role": "user", "content": user_input}]

    # For now, our loop has a single iteration, but each step is logged
    # individually so this still works once we add more iterations.
    _debug_step(debug, "THINKING", f"Deciding how to respond to:\n{user_input}")
    _debug_step(debug, "ACTION", "Calling Anthropic API (claude-haiku-4-5-20251001)")

    try:
        text = _call_claude(messages)
        _debug_step(debug, "RESULT", text)
    except anthropic.APIError as e:
        _debug_step(debug, "RESULT", f"Claude call failed ({e}), falling back to OpenAI")
        _debug_step(debug, "ACTION", "Calling OpenAI API (gpt-4o)")
        text = _call_openai(messages)
        _debug_step(debug, "RESULT", text)

    return text