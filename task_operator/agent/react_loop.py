"""Chapter 5 - The Agent Loop: Reason, Act, Observe.

The *deterministic shell* (this loop) owns:
  - the iteration limit (safety valve)
  - tool execution and error handling
  - the message history

The *probabilistic core* (brain.think) only decides what to think and which
tool to call next. Everything it "does" goes through tools.execute_tool().
"""

from __future__ import annotations

from task_operator.brain import new_client, think
from task_operator.config import get_config
from task_operator.tools import TOOLS, execute_tool


def _final_text(response) -> str:
    return "\n".join(b.text for b in response.content if b.type == "text").strip()


def react_loop(
    task: str,
    max_iterations: int | None = None,
    verbose: bool | None = None,
    client=None,
) -> str:
    """Run the ReAct loop until the model answers or max_iterations is hit.

    max_iterations and verbose come from config; pass them only to override
    (e.g. the book's max_iterations=2 boundary test). `client` is injectable
    so unit tests can pass a fake instead of calling the API.
    """
    config = get_config()
    if max_iterations is None:
        max_iterations = config["TASK_OPERATOR_MAX_ITERATIONS"]
    if verbose is None:
        verbose = config["TASK_OPERATOR_VERBOSE"]
    client = client or new_client()
    messages = [{"role": "user", "content": task}]

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n--- Iteration {iteration} ---")

        response = think(client, messages, TOOLS)

        # Reason: show what the model was thinking.
        if verbose:
            for block in response.content:
                if block.type == "thinking" and block.thinking:
                    print(f"Thought: {block.thinking}")
                elif block.type == "text" and block.text.strip():
                    print(f"Thought: {block.text.strip()}")

        # Keep the full content (thinking + tool_use blocks), not just the text.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            return "Error: the model declined this request."
        if response.stop_reason != "tool_use":
            return _final_text(response)

        # Act + Observe: run every requested tool, return all results in ONE message.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if verbose:
                print(f"Action: {block.name}({block.input})")
            result = execute_tool(block.name, block.input)
            if verbose:
                print(f"Observation: {result}")
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": result.startswith("Error:"),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "Error: max iterations reached without a final answer."
