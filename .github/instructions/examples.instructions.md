---
name: 'Examples and Demos'
description: 'Rules for example scripts and demo code'
applyTo: "examples/**/*.py"
---

Example code rules:

- Examples must be self-contained and runnable with `python examples/<name>.py`.
- Include clear comments explaining what the example demonstrates.
- Use `AgentConfig` for configuration; never hardcode API keys or endpoints.
- Print output in a human-readable format that shows the agent's response structure.
- Handle missing environment variables gracefully with a helpful error message.
- Keep examples minimal — demonstrate one concept per file.
