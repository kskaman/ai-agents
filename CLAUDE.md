# Project overview

This repo is a Python + Playwright test automation project.

# Core workflow

- Propose a plan before editing on any multi-file change.
- Always inspect existing patterns before creating new files.
- Prefer minimal diffs over broad refactors.
- After edits, run the smallest relevant verification first,
  then broader checks if needed.

# Commands

- Install: `pip install -r requirements.txt`
- Unit tests: `pytest tests/unit -q`
- E2E smoke: `pytest tests/e2e -m smoke -q`
- Lint: `ruff check .`

# Coding conventions

- Keep selectors inside page object files.
- Reuse existing helper methods before adding new ones.
- Avoid changing unrelated tests in the same task.

# Compact instructions

When using compact, preserve:

- files changed
- commands run
- failing tests and exact errors
- decisions already made
