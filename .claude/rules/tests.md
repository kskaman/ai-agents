---
paths:
  - "tests/**"
---

Apply these rules only when working on tests:

- Unit tests must never call the real API. Pass a fake client via `client=`
  (`FakeClient` and response helpers in `tests/unit/fakes.py`) and reuse it.
- Mirror the code layout: tests for `task_operator/tools/x.py` go in
  `tests/unit/tools/test_x.py`.
- Tests that hit the real API go behind `@pytest.mark.live`; they are skipped
  by default and run only when the user asks (`pytest -m live`).
- Keep assertions close to the action they validate.
- Assert on what the shell sends back to the model (messages, tool_result
  blocks), not just on the final string.
- For flaky behavior, add diagnostic logging before adding retries.
