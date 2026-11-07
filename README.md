## Claude files layout

- `CLAUDE.md` - holds only the always relevant-relevant project rules. It is loaded at project start and re-read after /compact. Keep it short.
- `.claude/rules/` - contains scoped instructions that apply only when Claude works on matching files or areas.
- `.claude/skills/` - holds reusable procedures and reference material. Skills load only when relevant - supporting files inside a skill stay out of context until needed.
- `.claude/agents/` - defines subagents with specific roles, tools, and model assignments.
- `.claude/settings.json` - holds permissions, hooks, and defaults - the enforceable part of your shell.
