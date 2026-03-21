---
applyTo: "src/**/*.py"
---

Python implementation rules for this project:

- Use explicit type hints and keep signatures stable.
- Keep business logic in small, testable units.
- Preserve Pydantic model contracts and structured response patterns.
- Do not bypass guardrails or observability wrappers.
- Add/adjust pytest tests for every functional change.
- Prefer dependency injection and configuration through `AgentConfig`.
- Handle failures with clear fallbacks; avoid silent exception swallowing.
