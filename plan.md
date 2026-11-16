# Task Operator backlog

## Chapter 5 - The Agent Loop

- [x] Tools: `calculate`, `get_weather` (stub), `count_characters`
- [x] `execute_tool` dispatcher that returns errors as strings
- [x] `react_loop` with Thought / Action / Observation output and `max_iterations`
- [x] Unit tests with a fake client (`tests/unit/agent/test_react_loop.py`)
- [x] Split into `agent/`, `brain/`, `tools/`, `config/` packages
- [ ] Live run: watch a multi-tool task end to end
- [ ] Exercise: add a `read_file(path)` tool, limited to the project folder
- [ ] Boundary test: question that needs no tool
- [ ] Boundary test: ambiguous task
- [ ] Boundary test: `max_iterations=2` on a multi-step task
- [ ] Boundary test: broken calculator (always raises); see how the model recovers
