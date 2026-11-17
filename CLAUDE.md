# Project overview

Task Operator: a Python agent built chapter by chapter from the book
"Building Agentic Systems". Code lives in `task_operator/`:

- `agent/` - the loop (Ch 5: `react_loop.py`); no API or tool details here
- `brain/` - model calls (`llm.py`, the only file that imports `anthropic`) and prompts
- `tools/` - one module per tool (function + `SCHEMA`), registered in `registry.py`
- `config/` - env variables, loaded and validated once at startup
- `cli/` - interactive chat (`chat.py`); keeps `history` across turns
- `__main__.py` - entry point: starts the chat (command-line arguments are rejected)

Architecture rule (Ch 4): the **deterministic shell** (our code) owns the
system prompt, tool set, iteration limit, tool execution and message history.
The **probabilistic core** (the model) only chooses thoughts and tool calls.

# Core workflow

- Propose a plan before editing on any multi-file change.
- Inspect existing patterns before creating new files.
- Prefer minimal diffs over broad refactors.
- After edits, run the smallest relevant verification first, then broader checks.
- Track chapter work and exercises in `plan.md`.
- When a change adds, removes or rewires a component, tool, config value or
  chat-turn step, update the diagrams in `docs/` in the same task (use the
  `update-diagrams` skill).

# Commands

- Install: `pip install -r requirements.txt`
- Unit tests: `pytest tests/unit -q` (no network, no API key needed)
- Live run (costs money, ask first): `python -m task_operator` (chat)
- Lint: `ruff check .`

# Coding conventions

- Model id is a single constant (`MODEL`) per module; never inline it.
- Tools never raise into the loop: `execute_tool` returns `"Error: ..."` strings
  and the loop marks them `is_error`.
- Append the full `response.content` to history, not just the text.
- Return all `tool_result` blocks for one turn in a single user message.
- Read env variables only through `task_operator.config.get_config()`; declare
  new ones in `ENV_VARS` (`task_operator/config/config.py`) and `.env.example`.
- The API client is injectable (`client=`) so tests use a fake.
- Avoid changing unrelated tests in the same task.

# Compact instructions

When using compact, preserve:

- files changed
- commands run
- failing tests and exact errors
- decisions already made
- current chapter and exercise in progress
