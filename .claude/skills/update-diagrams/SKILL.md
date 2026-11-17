---
name: update-diagrams
description: Update the Archify diagrams in docs/ after a code change that adds, removes or rewires a component, tool, config value, or a step of the chat turn. Use whenever architecture or the turn flow changes.
---

The diagrams are generated from JSON candidates kept in the repo:

| Candidate | Output | Shows |
|---|---|---|
| `docs/diagrams/architecture.json` | `docs/architecture.html` | modules and how they call each other |
| `docs/diagrams/chat-turn.json` | `docs/chat-turn.html` | one chat turn with a tool call |

Steps:

1. Make sure the code change is committed. Every box links to source lines
   at the commit in `meta.repository.revision`, and Archify verifies the
   citations against committed bytes.
2. Use the `archify` skill's authoring rules, then edit the candidate in place.
   - Update the boxes or messages, and keep each `sources` line range accurate.
     Get line numbers from `nl -ba <file>`.
   - Set `meta.repository.revision` to the new `git rev-parse HEAD`.
   - If a change needs a new diagram, add a row to the table above.
3. Finalize each changed diagram from the repo root. On this machine, Node
   22.15 reports a zero device ID from `fs.lstat`, which fails Archify's
   receipt check. Run Archify with Node 20 instead:

   ```bash
   N="$LOCALAPPDATA/nvm/v20.12.2/node.exe"
   A="C:/Users/kskam/.claude/skills/archify/bin/archify.mjs"
   "$N" "$A" finalize architecture docs/diagrams/architecture.json docs/architecture.html --repo-root . --quality showcase --json
   "$N" "$A" finalize sequence docs/diagrams/chat-turn.json docs/chat-turn.html --repo-root . --quality showcase --json
   ```

4. If a run fails, apply the fix its diagnostics name (`supportedFixes` /
   `nextAction`), then run it again.
5. Commit the candidate JSON and the HTML together. Check receipts
   (`docs/*.finalize*.json`, `*.browser-check.json`, `*.delivery.json`) are
   git-ignored.
