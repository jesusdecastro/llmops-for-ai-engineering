---
name: langfuse-tracing
description: "Instrument Python code with Langfuse @observe decorators and trace metadata for LLM observability. USE FOR: adding tracing to new functions, debugging missing spans, setting up trace metadata (session_id, user_id, tokens, latency). DO NOT USE FOR: prompt management (use prompt-versioning skill), evaluation (use evaluate-agent skill)."
---

# Langfuse Tracing Skill

Instrument Python code with Langfuse observability decorators and structured trace metadata.

## When to use this skill
- Adding `@observe` decorators to new LLM calls, tool functions, or guardrail scans.
- Debugging missing or incomplete trace spans.
- Setting up trace metadata capture (token counts, latency, session context).
- Verifying that existing instrumentation follows project conventions.

## Prerequisites
- `langfuse` package installed (`pip install langfuse`).
- Environment variables set: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`.

## Instrumentation patterns

### Basic function tracing
```python
from langfuse.decorators import observe

@observe(name="descriptive_function_name")
def my_function(query: str) -> str:
    # function implementation
    return result
```

### Adding trace metadata
```python
from langfuse.decorators import langfuse_context, observe

@observe(name="process_query")
def process_query(self, query: str, session_id: str, user_id: str) -> AgentResponse:
    start_time = time.time()
    # ... processing ...
    latency_ms = (time.time() - start_time) * 1000

    langfuse_context.update_current_observation(
        metadata={
            "session_id": session_id,
            "user_id": user_id,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "latency_ms": latency_ms,
            "model_id": self.config.model_id,
        }
    )
    return response
```

### Tool function tracing
```python
@observe(name="tool_search_catalog")
def search_catalog(query: str) -> list[dict]:
    results = _do_search(query)
    langfuse_context.update_current_observation(
        metadata={"results_count": len(results), "query": query}
    )
    return results
```

### Guardrail tracing
```python
@observe(name="scan_input")
def scan_input(self, text: str) -> tuple[str, bool, dict]:
    # ... scanning ...
    langfuse_context.update_current_observation(
        metadata={"is_safe": is_safe, "scanners_triggered": triggered}
    )
    return processed_text, is_safe, metadata
```

## Conventions for this project
- Every `@observe` must have a `name` parameter — never use the default.
- Name format: `<category>_<action>` (e.g., `tool_search_catalog`, `scan_input`, `llm_generate_response`).
- Always capture `session_id` and `user_id` when available.
- Always capture `input_tokens` and `output_tokens` for LLM calls.
- Guardrail scans must include `is_safe` or `is_valid` in metadata.
- Tool functions must include `results_count` in metadata.

## Verification
After adding instrumentation:
1. Run `make test` to verify no regressions.
2. Check that `@observe` imports are present.
3. Verify metadata keys match the conventions above.
