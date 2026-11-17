# Task Operator

An agent built chapter by chapter while reading "Building Agentic Systems".

```bash
pip install -r requirements.txt
pytest tests/unit -q                                   # offline, free
python -m task_operator     # chat (/help, /reset, /exit); needs ANTHROPIC_API_KEY in .env
```

## Diagrams

Open these in a browser; each box links to its source lines on GitHub.

- [docs/architecture.html](docs/architecture.html) - modules and how they call each other
- [docs/chat-turn.html](docs/chat-turn.html) - one chat turn with a tool call, step by step

They are generated with Archify from `docs/diagrams/*.json` and kept current
with the `update-diagrams` skill.

## Claude files layout

- `CLAUDE.md` - holds only the always-relevant project rules. It is loaded at session start and re-read after /compact. Keep it short.
- `.claude/rules/` - contains scoped instructions that apply only when Claude works on matching files (`tests.md` → `tests/**`).
- `.claude/skills/` - holds reusable procedures (`ship-check`: run with `/ship-check` before committing; `update-diagrams`: refresh `docs/` after architecture changes).
- `.claude/agents/` - defines subagents with specific roles, tools, and models (`researcher`, `reviewer`).
- `.claude/settings.json` - holds permissions and hooks, the enforceable part of the shell (auto-allow tests/lint, block `.env` files).
- `plan.md` - the backlog of chapter tasks and exercises.
