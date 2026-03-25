---
name: instrument
description: 'Add Langfuse @observe instrumentation to a function or module'
agent: 'observer'
tools:
  - search
  - read
  - editFiles
  - runInTerminal
---

# Add Langfuse Instrumentation

Add `@observe` decorators and trace metadata to a function or module.

## Input

Target: ${input:target:function name, file path, or module to instrument}

## Steps

1. **Read the target code** and identify all LLM calls, tool invocations, and guardrail scans.
2. **Add imports**: `from langfuse.decorators import observe` if not already imported.
3. **Add `@observe` decorators** with meaningful `name` parameters:
   - LLM calls: `@observe(name="llm_call_<purpose>")`
   - Tool functions: `@observe(name="tool_<tool_name>")`
   - Guardrail scans: `@observe(name="scan_input")` / `@observe(name="scan_output")`
4. **Add trace metadata** inside the function:
   ```python
   langfuse_context.update_current_observation(
       metadata={
           "session_id": session_id,
           "user_id": user_id,
           "input_tokens": usage.input_tokens,
           "output_tokens": usage.output_tokens,
           "latency_ms": latency_ms,
       }
   )
   ```
5. **Verify**: Run `make test` to ensure instrumentation doesn't break existing behavior.

## Output
List all functions instrumented and the metadata captured for each.
