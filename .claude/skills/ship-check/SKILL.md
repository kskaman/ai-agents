---
name: ship-check
description: Pre-commit checklist for the current changes.
disable-model-invocation: true
---

Run this only when the user explicitly asks.

1. Review `git diff --stat`
2. Run lint and the targeted tests for changed areas
3. Summarize remaining risk
4. Suggest a commit message
