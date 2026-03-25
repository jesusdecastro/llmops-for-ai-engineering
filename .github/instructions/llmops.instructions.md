---
name: 'LLMOps Observability'
description: 'Rules for Langfuse instrumentation, tracing, and prompt management'
applyTo: "src/**/*.py"
---

LLMOps and observability rules for this project:

- Every function that calls an LLM or tool must be decorated with `@observe` from `langfuse.decorators`.
- Include meaningful `name` parameter in `@observe` (e.g., `@observe(name="process_query")`).
- Capture trace metadata: `session_id`, `user_id`, `input_tokens`, `output_tokens`, `latency_ms`, `model_id`.
- Resolve system prompts from Langfuse via `client.get_prompt(name, label)` with a hardcoded fallback.
- Never inline long system prompts in Python code; store them in Langfuse and reference by name.
- When adding a new tool, include `@observe` on the tool function and log `results_count` in metadata.
- For guardrails, trace both `scan_input` and `scan_output` with `is_safe`/`is_valid` in metadata.
- Use `AgentConfig.langfuse_prompt_name` and `AgentConfig.langfuse_prompt_label` for prompt references.
- Cost tracking: log `input_tokens` and `output_tokens` on every LLM span for budget monitoring.
